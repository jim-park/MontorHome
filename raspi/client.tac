#!/usr/bin/env python

# Imports
import sys, os, json, time, re

from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.protocol import Factory
from twisted.internet.protocol import ReconnectingClientFactory as RCFactory
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.defer import inlineCallbacks
from twisted.protocols.basic import LineReceiver
from twisted.enterprise import adbapi
from twisted.application import service
from twisted.python import log

# Local imports
sys.path.insert(0, './pylib')
from Peer import Peer, Msg
from DB import DB

# Globals
LOGFILE     = './log/client.log'
DT          = "clnt"
DBPATH      = './db/data.db'
PEER_TYPE   = DT     # type for DB and Peer classes
LISTEN_PORT = 8001
APPSRV_PORT = 8007
APPSRV      = 'appserver'
#APPSRV = 'ec2-34-223-254-49.us-west-2.compute.amazonaws.com'

# Voltage conversion factor
# V = raw_data/CON_FACTOR
CON_FACTOR = 66.28611153

# to pass data between factories
queue      = []                 # message q between factories
getter     = None               # getter for message q


#
# extract Data from json sensor string
# return dict of sensor data
#
def extractJSONSensorData(jsonstr):
  ret = {}
  # {"sensor":[{"id":"0","val":"498","time":"1495833550"}]}
  try:
    obj = json.loads(jsonstr)
    sdata = obj['sensor'][0]
    ret['id']      = int(sdata['id'])
    ret['raw_val'] = int(sdata['val'])
    ret['time']    = int(sdata['time'])
    # Get voltage from raw ADC value
    ret['val']     = round(float(int(ret['raw_val']) / CON_FACTOR), 3)
  except Exception, e:
    ret = None
    log("Error: can't decode sensor data. Data ignored")
    #log("Error: e=%s" % e)
  return ret

#
# Check received line simple csum
# returns json string if ok
#
def chklinecsum(line):
  ret = False
  rxcsum  = int(line.split(' ')[1], base=16)
  jsonstr = line.split(' ')[0]
  if not chk_csum(jsonstr, rxcsum):
    log.msg("Error: simple csum failed. Data ignored")
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
  ret = 0;
  for c in data:
    ret += ord(c)
  return ret & 0xFF

#
# TCP Reconnecting Client Factory 
# Connects to remote app server
#
class txDataFactory(RCFactory):
  maxDelay = 1800  # 30 min
 
  def __init__(self):
    self._typ    = PEER_TYPE
    self.db      = DB(DBPATH, PEER_TYPE)  

    # TODO: something about this global
    global getter
    getter = self

  def buildProtocol(self, addr):
    p = Peer(self, self._typ, self.db)
    p.factory = self
    self.resetDelay()
    log.msg("connected to app server %s" % addr)
    return p

  def clientConnectionFailed(self, connector, reason):
    RCFactory.clientConnectionFailed(self, connector, reason)
    log.err("conn to appsrv failed %s" % reason)
    self.protocol = None

  def clientConnectionLost(self, connector, reason):
    RCFactory.clientConnectionLost(self, connector, reason)
    log.err("conn to appsrv lost %s" % reason)
    self.protocol = None

  # Send data onto peer, or store event
  def sendData(self):
    ret = None
    global queue
    while len(queue) > 0:
      data = queue.pop()
      # Are we connected to the app srv?
      if self.protocol and self.protocol.connected == 1:
        ret = self.protocol.txadd(data, tbl='data')
      else:
        log.msg('cache data event id [%d] in event table' % data['data_id']) 
        self.db.insertEvent('data', data['data_id'])
    return ret


#
# Protocol for incomming local ser2tcp TCP data
#
class rxDataProt(Protocol):

  def __init__(self, factory):
    self.factory = factory

  def dataReceived(self, data):
    for line in data.splitlines():
      log.msg("rx: %s" % line)
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

  def __init__(self):
    self._db  = DB(DBPATH, PEER_TYPE)

  def buildProtocol(self, addr):
    return self.protocol(self)

  # Wrapper for DB.insertDataGetRowId()
  def insertData(self, sdata):
    return self._db.insertDataGetRowId(sdata)


#
# Service for connection to app server from localclient
#
class AppServerTCPTXService(service.Service):

  def startService(self):
    log.msg("starting AppServerTCPTXService")
    reactor.connectTCP(APPSRV, APPSRV_PORT, txDataFactory())

  def stopService(self):
    log.msg("stopping AppServerTCPTXService")


#
# Service for ser2tcp recieved data
#
class Ser2TCPDataRXService(service.Service):

  def __init__(self):
    self.tx_factory  = None

  def startService(self):
    log.msg("starting Ser2TCPDataRXService")
    p = TCP4ServerEndpoint(reactor, LISTEN_PORT)
    p.listen(rxDataFactory())

  def stopService(self):
    log.msg("stopping Ser2TCPDataRXService")


##########################################################
# Main Application entry point
##########################################################
application = service.Application('locClnt')

ser2tcp_service = Ser2TCPDataRXService()
ser2tcp_service.setServiceParent(application)

appsrv_service = AppServerTCPTXService()
appsrv_service.setServiceParent(application)
