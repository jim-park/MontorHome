#!/usr/bin/env python

#######################################################################
#
#   Execute .tac files using twistd;
#     `twistd --pidfile=./<app_name>.pid -noy ./<app_name>.tac`
#
#      -noy; no-daemonise, no save state, run as python
#
#######################################################################


# Imports
import sys, os, re, md5, time, json, thread
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ServerEndpoint, SSL4ServerEndpoint
from twisted.internet import reactor, defer, ssl
from twisted.protocols.basic import LineReceiver
from twisted.enterprise import adbapi
from twisted.application import service
from twisted.python import log

# Local imports
PATH = '/opt/mh'
sys.path.insert(0, PATH + '/pylib')
from Peer import Peer, Msg, SLVE
from DB import DB

# Network
LISTEN_PORT = 8007  # For client connection
SSL_CERT_PATH = PATH + '/keys/cert.pem'
SSL_KEY_PATH = PATH + '/keys/srv_privkey.pem'

# DB
DB_PATH = PATH + '/db/data.db'

#
# Factory - Deal with incoming connections
#
class ClientRXDataFactory(Factory):
    protocol = Peer

    def __init__(self):
        self.typ = SLVE
        self.dbp = DB_PATH
        self.db = DB(self.dbp, self.typ)

    def startFactory(self):
        log.msg('waiting for connection')

    def stopFactory(self):
        log.msg('stopping ClientFactory')
        log.msg('ClientFactory ident: %d' % thread.get_ident())

    def buildProtocol(self, addr):
        log.msg("Got new connection %s" % addr)
        return Peer(self, self.typ, db=self.db)


#
# Service for TCP4ServerEndpoint
#
class ClientListenerService(service.Service):

    def startService(self):
        self._port = SSL4ServerEndpoint(reactor, LISTEN_PORT, ssl.DefaultOpenSSLContextFactory(
                                                            SSL_KEY_PATH, SSL_CERT_PATH))
        self._port.listen(ClientRXDataFactory())

    def stopService(self): pass
        # return self._port.stopListenting()

#
# Start here
#
application = service.Application('appsrv')
service = ClientListenerService()
service.setServiceParent(application)
