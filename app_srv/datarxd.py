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

#############
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
class Client_t(threading.Thread):

  def __init__(self, socket, name=None):
    threading.Thread.__init__(self)
    self._name   = name
    # Setup logging
    log.basicConfig(filename=LOGFILE,level=log.DEBUG, 
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s', 
                    datefmt='%m/%d/%Y %H:%M:%S')
    # Setup socket
    self._sock   = Sock(sock=socket, log=log)
    self._db     = SQLiteDB(log=log)
    log.info("Client: init'd")


  #
  # Thread startup
  #
  def start(self):
    log.info("Client: verify new conn")
    if self._verify():
      log.info("Client: new conn verified OK")
      
      # open local db
      log.info("Client: connect to local DB")
      if not self._db.open():
        log.error("Client: failed to open db")
        self._stop()
        return
 
      log.info("Client: connected to local DB")
      log.info("Client: get DB csum")
      self._db.csum()
      log.info("Client: DB csum: %s" % self._db.csum())
            
    else:
      log.info("Client: Failed to verify new conn!")
      self._stop()
    

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
  
   
  #
  # Verify new client connection is allowed
  #
  def _verify(self):
    if self._sock:
      idstr = self._sock.recv()
      # can't continue without the id string
      if not idstr: return False

      log.info("Client - id: %s, len: %d" % (idstr, len(idstr))) 
      
      # sanatise and extract data
      p = re.compile('id:(\d),(\w{16})') 
      m = p.search(idstr)
      if m:
        msgid = int(m.group(1))
        msgpw = str(m.group(2))
        for client in CLIENTS:
          # Verify from 'id' : 'password' list
          for id, pw in client.iteritems():
            id = int(id)
            pw = str(pw)
            #log.info("CLIENTS: id: %d, p: %s" % (id, pw))
            #log.info("MESSAGE: id: %d, p: %s" % (msgid, msgpw))
            if msgid == id and msgpw == pw:
              log.info("Client - connection Verified ok")
              return True
            if msgid != id or msgpw != pw: 
              log.warning("Client - connection failed verification!")
              return False
      else:
        # Not valid, reject
        log.warning("Client - bad idstr [%s] from %s" % (msg, sock.getpeername()))
        return False
      


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
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s', 
                    datefmt='%m/%d/%Y %H:%M:%S')

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
    for t, port in self._client_t.iteritems():
      log.info("srv - joining thread %s" % port)
      t.join()
      log.info("srv - joined thread %s" % port)
      
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
    # Start a client thread
    t = Client_t(clientsocket, str(port))
    t.start()
    self._client_t[str(port)] = t
    log.info("srv - client thread started")


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
