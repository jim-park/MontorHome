#!/usr/bin/env python

#######################################################################
#
#   Execute .tac files using twistd;
#     `twistd --pidfile=./<app_name>.pid -noy ./<app_name>.tac`
#
#      -noy; no-daemonise, no save state, run as python
#
#######################################################################

# System imports
import json
from OpenSSL import SSL
from twisted.internet import reactor, defer, ssl
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet.protocol import ReconnectingClientFactory as RCFactory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.application import service
from twisted.logger import Logger
from twisted.python.log import ILogObserver

# Libmh imports
from libmh import MSTR
from libmh.db import SQLite3DB
from libmh.peer import Peer
from libmh.mhlog import mhlogger

# Globals
BASEPATH = '/opt/mh'
LOGFILE = BASEPATH + '/log/client.log'
DT = "clnt"
DBPATH = BASEPATH + '/db/data.db'
PEER_TYPE = MSTR  # type for DB and Peer classes

# Network
LISTEN_PORT = 8001
# APPSRV = 'ec2-34-223-254-49.us-west-2.compute.amazonaws.com'
APPSRV = '192.168.8.101'
APPSRV_PORT = 8007
SSL_CERT_PATH = BASEPATH + '/keys/cert.pem'
SSL_KEY_PATH = BASEPATH + '/keys/clnt_key.pem'

# Voltage conversion factor
# V = raw_data/CON_FACTOR
CON_FACTOR = 66.28611153

# to pass data between factories
queue = []  # message q between factories
getter = None  # getter for message q


#
# extract Data from json sensor string
# return dict of sensor data
#
def extractJSONSensorData(jsonstr):
    log = Logger()
    ret = {}
    # {"sensor":[{"id":"0","val":"498","time":"1495833550"}]}
    try:
        obj = json.loads(jsonstr)
        sdata = obj['sensor'][0]
        ret['sens_id'] = int(sdata['id'])
        ret['raw_val'] = int(sdata['val'])
        ret['time'] = int(sdata['time'])
        # Get voltage from raw ADC value
        ret['val'] = round(float(int(ret['raw_val']) / CON_FACTOR), 3)
    except Exception, e:
        ret = None
        log.error("Error: can't decode sensor data. Data ignored", system='extjsondata')
        # log("Error: e=%s" % e)
    return ret


#
# Check received line simple csum
# returns json string if ok
#
def chklinecsum(line):
    log = Logger()
    ret = False
    rxcsum = int(line.split(' ')[1], base=16)
    jsonstr = line.split(' ')[0]
    if not chk_csum(jsonstr, rxcsum):
        log.error("Error: simple csum failed. Data ignored", system=chklinecsum)
    else:
        ret = jsonstr
    d = defer.Deferred()
    reactor.callWhenRunning(d.callback, ret)
    return d


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
    ret = 0
    for c in data:
        ret += ord(c)
    return ret & 0xFF


#
# SSL Context Factory
#
class clientSSLCtxFactory(ssl.ClientContextFactory):

    def getContext(self):
        self.method = SSL.SSLv23_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file(SSL_CERT_PATH)
        ctx.use_privatekey_file(SSL_KEY_PATH)
        return ctx


#
# TCP Reconnecting Client Factory 
# Connects to remote app server
#
class txDataFactory(RCFactory):
    maxDelay = 1800  # 30 min
    log = Logger()

    def __init__(self):
        self.db = SQLite3DB(DBPATH, PEER_TYPE)

        # TODO: something about this global
        global getter
        getter = self

    def buildProtocol(self, addr):
        p = Peer(self, PEER_TYPE, self.db)
        p.factory = self
        self.resetDelay()
        self.log.debug("connected to app server {addr}", addr=addr, system='clienttx')
        self.protocol.connected = 1
        return p

    def clientConnectionFailed(self, connector, reason):
        RCFactory.clientConnectionFailed(self, connector, reason)
        self.log.warn(_stuff="conn to appsrv failed", _why=reason, system='clienttx')
        self.protocol = None

    def clientConnectionLost(self, connector, reason):
        RCFactory.clientConnectionLost(self, connector, reason)
        self.log.error(_stuff="conn to appsrv lost", _why=reason, system='clienttx')
        self.protocol = None

    # Send data onto peer
    def sendData(self):
        ret = None
        global queue
        while len(queue) > 0:
            data = queue.pop()
            # Are we connected to the app srv?
            if self.protocol and self.protocol.connected == 1:
                ret = self.protocol.txadd(data, tbl='data')
        return ret


#
# Protocol for incomming local ser2tcp TCP data
#
class rxDataProt(Protocol):
    log = Logger()

    def __init__(self, factory):
        self.factory = factory

    def dataReceived(self, data):
        for line in data.splitlines():
            self.log.debug("rx: {line}", line=line)
            d = defer.Deferred()
            d = chklinecsum(line)
            d.addCallback(extractJSONSensorData)
            d.addCallback(self.factory.insertData)
            d.addCallback(self.appendTXQ)

    def appendTXQ(self, sdata):
        global queue
        queue.append(sdata)
        if getter is not None:
            getter.sendData()
        return True


#
# Factory for ser2tcp local TCP connection
#
class rxDataFactory(Factory):
    protocol = rxDataProt
    log = Logger()

    def __init__(self):
        self._db = SQLite3DB(DBPATH, PEER_TYPE)

    def buildProtocol(self, addr):
        return self.protocol(self)

    # Wrapper for DB.insertdatagetid()
    def insertData(self, sdata):
        return self._db.insertdatagetid(sdata)


#
# Service for connection to app server from localclient
#
class AppServerTCPTXService(service.Service):
    log = Logger()

    def startService(self):
        self.log.info("starting AppServerTCPTXService", system="client")
        reactor.connectSSL(APPSRV, APPSRV_PORT, txDataFactory(), clientSSLCtxFactory())

    # def stopService(self):
    #     self.log.info("stopping AppServerTCPTXService")


#
# Service for ser2tcp recieved data.
# We bind, ser2tcp connects.
#
class Ser2TCPDataRXService(service.Service):
    log = Logger()

    def __init__(self):
        self.tx_factory = None

    def startService(self):
        self.log.info("starting Ser2TCPDataRXService", system="ser2tcp listener")
        p = TCP4ServerEndpoint(reactor, LISTEN_PORT)
        p.listen(rxDataFactory())

    # def stopService(self):
    #     log.msg("stopping Ser2TCPDataRXService")


##########################################################
# Main Application entry point
##########################################################
application = service.Application('client')
application.setComponent(ILogObserver, mhlogger('client'))

ser2tcp_service = Ser2TCPDataRXService()
ser2tcp_service.setName('rxserdata')
ser2tcp_service.setServiceParent(application)

appsrv_service = AppServerTCPTXService()
appsrv_service.setServiceParent(application)
