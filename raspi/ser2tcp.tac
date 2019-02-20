#!/usr/bin/env python

#######################################################################
#
#   Execute .tac conf using twistd;
#     `twistd --pidfile=./<app_name>.pid -noy ./<app_name>.tac`
#
#      -noy; no-daemonise, no save state, run as python
#
#######################################################################

__author__ = "James Park"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"

import time, os, json
from twisted.internet import reactor, task
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.protocol import ReconnectingClientFactory as RCFactory
from twisted.internet.serialport import SerialPort
from twisted.protocols.basic import LineReceiver
from twisted.application import service
from twisted.python import log

# Globals
DTSER = 'ser rx'
DTTCP = 'tcp tx'
PATH = '/opt/mh'
LOGFILE = PATH + '/log/ser2tcp.log'
SRV = 'localhost'

# Config
# TODO: put this in an external config file
BAUDRATE = 9600
REQ_PERIOD = 30  # request period for sensor data (secs)

queue = []  # message q between factories
getter = None  # getter for message q


#
# list devices starting '/dev/ttyACM' or '/dev/ttyUSB'
# 
def getSerialPorts():
    import re
    ports = []
    dir = '/dev/'
    r = re.compile('tty(USB|ACM)\d{0,2}')
    for path in os.listdir(dir):
        m = re.match(r, path)
        if m:
            ports.append(dir + m.group(0))
    return ports


#
# Check simple csum against data
#
def chk_csum(data, csum):
    ret = False
    data_csum = simpl_csum(data)
    if data_csum == csum:
        ret = True
    return ret


#
# Calculate simple csum
#
def simpl_csum(data=None):
    ret = False
    if not data: return ret
    ret = 0;
    for c in data:
        ret += ord(c)
    return ret & 0xFF


#
# TCP Client Protocol 
#
class TCPDataProtocol(Protocol):
    def connectionMade(self):
        log.msg("connected to local client", system=DTTCP)
        global getter
        getter = self

    def connectionLost(self, reason):
        log.msg("disconnected from local client", system=DTTCP)
        global getter
        getter = None

    def sendData(self):
        while len(queue) > 0:
            data = queue.pop()
            log.msg("%s" % data, system=DTTCP)
            self.transport.write(data + '\n')


#
# TCP Reconnecting Client Factory
# Connects to local client
#
class TCPDataTXFactory(RCFactory):
    maxDelay = 1800  # 30 min

    def buildProtocol(self, addr):
        log.msg("connected to local client %s" % addr, system=DTTCP)
        self.resetDelay()
        return TCPDataProtocol()

    def startedConnecting(self, connector):
        log.msg("attempting to connect to local client", system=DTTCP)

    def clientConnectionFailed(self, connector, reason):
        log.msg('tcp connection to local client failed', system=DTTCP)
        # log('e=%s' % reason)
        RCFactory.clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        log.msg('tcp connection to local client lost', system=DTTCP)
        # log('e=%s' % reason)
        RCFactory.clientConnectionLost(self, connector, reason)


#
# Service for TCP Client to send data
#
class TCPDataTXService(service.Service):
    def startService(self):
        log.msg("starting TCPDataTXService", system=DTTCP)
        f = TCPDataTXFactory()
        reactor.connectTCP(SRV, 8001, f)


#
# Serial port data Protocol
#
class SerialDataProtocol(LineReceiver):
    def __init__(self, factory, spath):
        self.factory = factory
        self.spath = spath
        self.reqtask = task.LoopingCall(self.requestSerialData)

        self.makeTransport()

    def makeTransport(self):
        try:
            LineReceiver.makeConnection(self, SerialPort(self, self.spath, reactor))
        except Exception, e:
            log.err('failed to connect transport to %s e=%s' % (self.spath, e), system=DTSER)
            self.factory.connectionFailed(e)

    def connectionMade(self):
        log.msg('connected to %s ok' % self.spath, system=DTSER)
        self.factory.resetDelay()
        if not self.reqtask.running:
            self.reqtask.start(REQ_PERIOD)

    def connectionLost(self, reason):
        log.msg('connection lost e=%s' % reason, system=DTSER)
        if self.reqtask.running:
            self.reqtask.stop()
        self.factory.connectionLost(reason)

    def connectionFailed(self, reason):
        log.msg('connection failed e=%s' % reason, system=DTSER)
        if self.reqtask.running:
            self.reqtask.stop()
        self.factory.connectionFailed(reason)

    def requestSerialData(self):
        self.transport.writeSomeData('r')

    # Put rx'd data in the Q
    def lineReceived(self, line):
        log.msg("%s" % line, system=DTSER)

        # Extract and check simple csum
        rxcsum = int(line.split(' ')[1], base=16)
        jsonstr = line.split(' ')[0] + ' '
        if not chk_csum(jsonstr, rxcsum):
            log.err("Error: simple csum failed. Data ignored", system=DTSER)
            return

        # Put timestamp on data
        jsonobj = json.loads(jsonstr)
        jsonobj['sensor'][0]['time'] = "%d" % int(time.time())
        jsontstr = json.dumps(jsonobj, separators=(',', ':'))

        # Append simple csum
        csum = simpl_csum(jsontstr)
        txdata = jsontstr + ' %02X' % csum

        # Add to the queue for sending
        queue.append(txdata)
        if getter is not None:
            getter.sendData()
        else:
            log.msg('no tcp connection. Data buffered [%d]' % len(queue), system=DTSER)


# log.msg('data: %s' % txdata)



#
# Serial Factory
#
class SerialDataRXFactory(ClientFactory):
    protocol = SerialDataProtocol
    maxDelay = 300.0
    factor = 2.7182818284590451  # (math.e)
    initialDelay = 1.0

    def __init__(self):
        self.idx = 0
        self.delay = self.initialDelay

    def buildProtocol(self):
        devs = getSerialPorts()
        # Check at least one serial device exists
        if len(devs) == 0:
            log.err("no serial dev found", system=DTSER)
            self.connectionFailed('no serial dev found')
            return None

        # increment index, and keep index in range
        self.idx += 1
        if self.idx > len(devs) - 1: self.idx = 0

        # try to connect protocol to device
        p = self.protocol(self, devs[self.idx])
        p.factory = self
        return p

    def connectionFailed(self, reason):
        log.msg('connection to serial port failed', system=DTSER)
        self.reconnectSerial()

    def connectionLost(self, reason):
        log.msg('connection to serial port lost', system=DTSER)
        self.reconnectSerial()

    def resetDelay(self):
        self.delay = self.initialDelay

    def reconnectSerial(self):
        self.delay = min(self.delay * self.factor, self.maxDelay)
        log.msg('reconnect to serial port in %0.2f secs' % self.delay, system=DTSER)
        reactor.callLater(self.delay, self.buildProtocol)


#
# Service for serial data received
#
class SerialDataRXService(service.Service):
    factory = SerialDataRXFactory

    def startService(self):
        log.msg("serServ: starting SerialDataRXService", system=DTSER)
        f = self.factory()
        f.buildProtocol()


##########################################################
# Main Application entry point
##########################################################
application = service.Application('tcp2ser')

serdata_service = SerialDataRXService()
serdata_service.setServiceParent(application)

locclnt_service = TCPDataTXService()
locclnt_service.setServiceParent(application)
