#!/usr/bin/env python


# Imports
import sys, os, re, md5, time, json
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor, defer
from twisted.protocols.basic import LineReceiver
from twisted.enterprise import adbapi
# Local imports
#from DB import DB
sys.path.insert(0, './pylib')
from Peer import Peer, Msg


#
# Factory - Deal with incomming connections
#
class Factory(Factory):
  # This will be used by the default buildProtocol
  # to create new protocols:
  protocol = Peer 
 
  def __init__(self, logFile='./log/srv.log'):
    self.lf = logFile

  def startFactory(self):
    self.fp = open(self.lf, 'a')
    self.log('waiting for connection')

  def stopFactory(self):
    self.fp.close()

  def buildProtocol(self, addr):
    self.log("Got new connection %s" % addr)
    #return SrvPeer(self, self.fp)
    return Peer(self, 'srv', self.fp)

  def log(self, msg):
    if msg:
      self.fp.write("srv  %s\n" % msg)
      self.fp.flush()

# Main
if __name__ == '__main__':
  endpoint = TCP4ServerEndpoint(reactor, 8007)
  endpoint.listen(Factory())
  reactor.run()
  sys.exit(0)
