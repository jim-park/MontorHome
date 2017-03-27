#!/usr/bin/env python

####################################################################
#
# Daemon to recieve sensor data from vehicle.
# Open ssl socket.
# Accept and verify connection
# Check DBs are synced - send csum
# Wait for data
# Insert data into DB - send csum
# Periodically check DB is synced
#
####################################################################

import sqlite3, sys, time
import socket, select
import logging as log
import threading
import re
# custom imports
sys.path.insert(0, './pylib')
from Daemon import Daemon
from Sock import Sock
from SQLiteDB import SQLiteDB
from Prot import Prot


# Global constants
NAME    = 'datarxd'
LOGFILE = './log/datarxd.log'
PIDFILE = './run/datarxd.pid'
DBFILE  = './db/data.db'
PORT    = 4867
IDSTRLEN  = 21

CLIENTS = [ { "0" : "iw9foj5ojv4dg2vd" }]



##################################################
# Class to handle a client connection
# Run as a thread
##################################################

class Client_t(Prot):
  
  #
  # Initialise
  #
  def __init__(self, sock, name=None, log=None):
    Prot.__init__(self, 'srv', sock=sock, name=name, log=log, cred=CLIENTS)
    
  #
  # Stop this thread
  #
  def _stop(self):
    log.info("Client: Stopping")
    # self.stop()

  #
  # Run
  #   
  def run(self):
    log.info("Client: running")
    msg = self._sock.recv()
    if msg and msg == 'dbinit': self.dbinit()
    
    log.info("Client: ran")
  

#############################################
# Handle client connections and manage threads 
# ###########################################
class DataRXd(Daemon):

  def __init__(self):
    Daemon.__init__(self, pidfile=PIDFILE, name=NAME)
    # Daemon config
    self._name       = NAME
    self._client_t   = {}
    # DB config 
    self._db_path    = DBFILE
    self._db         = None
    # Socket
    self._sock       = None
    
    # Setup logging
    log.basicConfig(filename=LOGFILE,level=log.DEBUG, 
                    format='%(asctime)s.%(msecs)03d '\
                           '%(levelname)s %(message)s', 
                           datefmt='%m/%d/%y %H:%M:%S')

  #
  # Start
  #
  def _start(self):
    log.info("srv - Starting")
    # Open socket
    if self._sock is None:
      try:
        # TODO: wrap the socket in ssl 
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((socket.gethostname(), PORT))
        self._sock.listen(5)
        log.info("srv - Socket listening on port %d" % PORT)
      except Exception, e:
        # Bail out if we can't open socket
        log.error("srv - Could not open socket on port %s. [e=%s]" % (PORT, e))
        self.stop() 
 
  #
  # Stop
  #
  def _stop(self):
    log.info("srv - Stopping")
    # TODO: make threads stop neatly
    '''
    for t, port in self._client_t.iteritems():
      log.info("srv - joining thread %s" % (t))
      if port._started: port.join(1)
      log.info("srv - joined thread %s" % port)
    '''  
    if self._sock is not None:
      self._sock.close()
      log.info("srv - Closed listening socket")
    log.info("srv - Stopped")

  #
  # Main run loop
  #
  def _run(self):
    log.info("srv - waiting for connection")
    # Sit and wait for client connections
    try:
      (clientsocket, address) = self._sock.accept()
    except Exception, e:
      log.error("srv - Couldn't accept conn. [e=%s]" % e)
      self.stop()

    # Accepted connection
    port = address[1]
    log.info("srv - Got new conn from %s %s" % (address[0], port))
    clientsocket.setblocking(0)
    # Start a new connection thread
    t = Client_t(clientsocket, port, log=log)
    t.start()
    self._client_t[str(port)] = t
    log.info("srv - client thread started")

   
    log.info("srv - Exiting")
    self.stop()
    sys.exit(0)

#
# Process entry point
#
if __name__ == "__main__":
  datarxd = DataRXd()

  if len(sys.argv) == 2:
    if 'start' == sys.argv[1]:
      datarxd.start()
    elif 'restart' == sys.argv[1]:
      datarxd.restart()
    elif 'stop' == sys.argv[1]:
      datarxd.stop()
    else:
      print "Unknown command"
      sys.exit(2)
    sys.exit(0)
  else:
    print "usage %s start|stop|restart" % sys.argv[0] 
    sys.exit(2)
