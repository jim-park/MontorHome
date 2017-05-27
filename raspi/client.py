#!/usr/bin/env python

# Imports
import sys, os, json, time, re
from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.protocol import Factory
from twisted.internet.protocol import ReconnectingClientFactory as RCFactory
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.protocols.basic import LineReceiver
from twisted.enterprise import adbapi
# Local imports
sys.path.insert(0, './pylib')
from Peer import Peer, Msg
from DB import DB

# Globals
LOGFILE = './log/client.log'
DT = "clnt"
#APPSRV = 'ec2-34-223-254-49.us-west-2.compute.amazonaws.com'
APPSRV = 'localhost'
DBPATH = './db/data.db'

# Conversion factor
# data = raw_data/CON_FACTOR
CON_FACTOR = 66.28611153



#
# Log stuff
#
def log(msg):
  try:
    f = open(LOGFILE, "a")
  except Exception, e:
    sys.stderr.write("could not open logfile")
  tm_str = time.strftime('%y/%m/%d %H:%M:%S')
  log_str = "%s %s - %s\n" % (tm_str, DT, msg)
  f.write(log_str)
  f.close()

#
# extract Data from json sensor string
# return dict of sensor data
#
def extractJSONSensorData(jsonstr):
  ret = {}
  # {"sensor":[{"id":"0","val":"498","time":"1495833550"}]}
  try:
    obj = json.loads(jsonstr)
    sensor_data = obj['sensor'][0]
    ret['id']      = int(sensor_data['id'])
    ret['raw_val'] = int(sensor_data['val'])
    ret['time']    = int(sensor_data['time'])
    # Get voltage from raw ADC value
    ret['val']     = float(int(ret['raw_val']) / CON_FACTOR)
    #log('sensor id: %d, raw_val %d, val %0.2f, time %d' %\
    #    (ret['id'], ret['raw_val'], ret['val'], ret['time']))
  except Exception, e:
    ret = None
    log("Error: can't decode sensor data. Data ignored")
    #log("Error: e=%s" % e)
  return ret


#
# Check received line simple csum
# returns json string if ok
#
def linecsum(line):
  ret = False
  rxcsum  = int(line.split(' ')[1], base=16)
  jsonstr = line.split(' ')[0]
  if not chk_csum(jsonstr, rxcsum):
    log("Error: simple csum failed. Data ignored")
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
 
  def __init__(self, logFile=LOGFILE):
    # TODO: sort out shambolic log file handle
    self._lf         = logFile
    self._lfp        = open(self._lf, 'a')
    self._clnt_peer = None
    self._typ       = 'clnt'
    self.dbp        = './db/data.db'
    self.db         = DB(self.dbp, self._typ, self._lfp)

  def startedConnecting(self, connector):
    log("attempting to connect to app server")

  def buildProtocol(self, addr):
    log("connected to app server %s" % addr)
    self.resetDelay()
    self._clnt_peer = Peer(self, self._typ, self._lfp)
    return self._clnt_peer

  def clientConnectionFailed(self, connector, reason):
    log("connection to app server failed")
    #log("e=%s" % reason)
    RCFactory.clientConnectionFailed(self, connector, reason)
  
  def clientConnectionLost(self, connector, reason):
    log("connection to app server lost")
    #log("e=%s" % reason)
    RCFactory.clientConnectionLost(self, connector, reason)

  # Pass data onto peer
  def txadd(self, data):
    ret = None
    # If we're connected to the app srv;
    # send data to app srv
    if self.protocol and self.protocol.connected == 1:
      ret = self._clnt_peer.txadd(data)
    else:
      log('app srv not available')
      log('storing data_id [%d] in event table' % data['data_id']) 
      # leave an entry in event table
      self.db.insertEvent('data', data['data_id'])
    return ret

#
# Protocol for incomming ser2tcp local TCP data
#
class rxDataProt(Protocol):

  def __init__(self, factory):
    self.factory = factory

  def connectionMade(self):
    #self.transport.write("ser2tcp connected ok\n")
    log("ser2tcp: %s %s connected" % self.transport.client)

  def connectionLost(self, reason):
    log("connection to ser2tcp lost e=%s" % (reason))
  
  # deal with data rx'd from ser2tcp in json format thus;
  def dataReceived(self, data):
    for line in data.splitlines():
      log("rx: %s" % line)
      d = defer.Deferred()
      d = linecsum(line)
      d.addCallback(extractJSONSensorData)
      # insert rx'd sensor data into local DB
      d.addCallback(self.factory.insertGetRowId)
      d.addCallback(self.factory.txData)

#
# Factory for ser2tcp local TCP connection
#
class rxDataFactory(Factory):
  protocol = rxDataProt

  def __init__(self, txdatafactory):
    self._txdatafct = txdatafactory
    # TODO, get rid of this logfileh horribleness.
    self._db     = DB(DBPATH, 'clnt', open(LOGFILE, 'a'))

  def buildProtocol(self, addr):
    return rxDataProt(self)

  #
  # Wrapper for db method
  #
  def insertGetRowId(self, data):
    return self._db.insertGetRowId(data)

  #
  # Wrapper for txDataFactory.txadd()
  #
  def txData(self, data):
    return self._txdatafct.txadd(data)



##########################################################
# Main entry point
##########################################################
def main():
  tx_f = txDataFactory()
  # Connect to app srv
  reactor.connectTCP(APPSRV, 8007, tx_f)
  
  # Start local listener for ser2tcp rx'd data
  rx_f = TCP4ServerEndpoint(reactor, 8001)
  rx_f.listen(rxDataFactory(tx_f))

  reactor.run()
  sys.exit(0)

#
# Call main()
#
if __name__ == '__main__': main()
