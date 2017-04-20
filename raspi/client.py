#!/usr/bin/env python

# imports
import sys, os, json, time, re
from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.protocols.basic import LineReceiver
from twisted.enterprise import adbapi
# local imports
sys.path.insert(0, './pylib')
from Peer import Peer, Msg

# Globals
LOGFILE = './log/client.log'
DT = "clnt"

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

##########################################################
# Factory - Make kick off connection to app server
##########################################################
class Factory(ClientFactory):
  # This will be used by the default buildProtocol
  # to create new protocols:
 
  def __init__(self, logFile=LOGFILE):
    self.lf         = logFile
    self.lfp        = None
    self._clnt_peer = None

  def startedConnecting(self, connector):
    self.lfp = open(self.lf, 'a')
    log("start connection")

  # Got connection, build prot on it
  def buildProtocol(self, addr):
    log("connected to %s" % (addr))
    self._clnt_peer = Peer(self, 'clnt', self.lfp)
    return self._clnt_peer

  # Connection failed 
  def clientConnectionFailed(self, connector, reason):
    log("connection to app server failed: %s" % reason)
    # TODO: Retry connect
  
  def clientConnectionLost(self, connector, reason):
    log("connection to app server lost: %s" % reason)
    # TODO: Retry connect

  # Log stuff
  def log(self, msg):
    if msg:
      self.lfp.write("clnt  %s\n" % msg)
      self.lfp.flush()

  # Pass event onto peer
  def eventrx(self):
    self._clnt_peer.doevent()

# Handle incoming event publisher connections
class EvPublisher(Protocol):

  def __init__(self, factory):
    self.factory = factory

  def connectionMade(self):
    self.transport.write("connected as pubisher ok\n")
    log("publisher %s %s connected" % self.transport.client)

  def connectionLost(self, reason):
    log("connection lost to publisher %s %s" % self.transport.client)
  
  def dataReceived(self, data):
    log("event from %s %s" % self.transport.client)
    p = re.compile("^EV.*$")
    m = p.search(data)
    if m:
      self.factory.informSubscribers()

class Event(Factory):

  def __init__(self, app_srv_fct):
    self.srv_fct = app_srv_fct

  def buildProtocol(self, addr):
    return EvPublisher(self)

  def informSubscribers(self):
    log("event handler: enent received")
    self.srv_fct.eventrx()


##########################################################
# Main
##########################################################
if __name__ == '__main__':
  clnt_fct = Factory()
  # Connect to app srv
  reactor.connectTCP('comp1', 8007, clnt_fct)
  
  # Start local event listener
  ev = TCP4ServerEndpoint(reactor, 8001)
  ev.listen(Event(clnt_fct))

  reactor.run()
  sys.exit(0)
