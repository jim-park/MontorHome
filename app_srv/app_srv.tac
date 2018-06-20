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
from twisted.python.log import ILogObserver
from twisted.python.logfile import DailyLogFile
from twisted.application import service
# from twisted.python import log
from twisted.logger import Logger
# Local imports
from libmh.peer import Peer, Msg, SLVE
from libmh.db import MySQLDB
from libmh.mhlog import mhlogger

# Application base path
PATH = '/opt/mh'

# Network config
LISTEN_PORT = 8007  # For client connection
SSL_CERT_PATH = PATH + '/keys/cert.pem'
SSL_KEY_PATH = PATH + '/keys/privkey.pem'

# DB config
DB_PATH = PATH + '/db/data.db'
DB_NAME = 'mh_data'
DB_USER = None
DB_PASS = None


#
# Factory - Deal with incoming connections
#
class ClientRXDataFactory(Factory):
    protocol = Peer
    log = Logger()

    def __init__(self):
        self.typ = SLVE
        self.dbp = DB_PATH
        self.db = MySQLDB(self.dbp, self.typ)

    def startFactory(self):
        self.log.info('waiting for remote to connect', system='clientrxfact')

    def buildProtocol(self, addr):
        self.log.info("Got new connection from: {addr}", addr=addr, system='clientrxfact')
        return Peer(self, self.typ, db=self.db)


#
# Service for TCP4ServerEndpoint
# This starts a ClientRXFactory to wait for a new client connection.
#
class ClientListenerService(service.Service):

    def startService(self):
        self._port = SSL4ServerEndpoint(reactor, LISTEN_PORT, ssl.DefaultOpenSSLContextFactory(
                                                            SSL_KEY_PATH, SSL_CERT_PATH))
        self._port.listen(ClientRXDataFactory())


#
# Start here
#

# Create application and configure logging
application = service.Application('appsrv')
application.setComponent(ILogObserver, mhlogger('appsrv'))
# Create services
service = ClientListenerService()
service.setServiceParent(application)
