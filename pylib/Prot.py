#!/usr/bin/env python

import threading, sys, os
import time
import logging as log
import re

# Custom imports
sys.path.insert(0, './pylib')
from Sock import  Sock
from SQLiteDB import SQLiteDB


DT = 'prot - '
#
# Generic Protocol for bot ends of
# an MH connection
#
class Prot(threading.Thread):

  def __init__(self, type, sock=None, name=None, srv=None, prt=None, log=None, cred=None):
    threading.Thread.__init__(self)
    self._type      = type
    self._name      = name
    self._appsrv    = srv
    self._srvpt     = prt
    self._cred      = cred
    # Setup DB 
    self._db        = SQLiteDB(log=log)
    # Setup socket
    if sock:
      self._sock    = Sock(sock=sock, log=log)
    elif srv and prt:
      self._sock    = Sock(host=self._appsrv, port=self._srvpt, log=log)
    else:
      log.error(DT+"cannot setup socket, no sock or srv or prt")


  
  #
  # Thread startup
  #
  def start(self):
    log.info(DT+"verify connection")
    if self._verify():
      log.info(DT+"connection verified ok")
      ''' 
      # open local db
      log.info(DT+"connect to local DB")
      if not self._db.open():
        log.error(DT+"failed to open db")
        self._stop()
        return
 
      log.info(DT+"connected to local DB")
      log.info(DT+"get DB csum")
      self._db.csum()
      log.info(DT+"DB csum: %s" % self._db.csum())
      '''  
 
    else:
      log.info(DT+"Failed to verify new conn!")
      log.warning(DT+"Exiting")
      self.stop()
      sys.exit(0)

  #
  # Stop
  #
  def stop(self): pass
    # Close DB conn
    # Close Socket
    # Join this thread


  #
  # Verify new connection is allowed
  #
  def _verify(self):
    ret = False
    if self._sock:
      # Are we a remote client?
      if self._type == 'rem':
        # Send ID string to app srva
        self._sock.send(self._cred)
        time.sleep(2)

      # srv and client
      # Wait for a response
      msg = self._sock.recv()
        
      if msg:
        log.debug(DT+"msg %s, type %s" % (msg, self._type)) 
        # sanatise and extract data
        idstr_p = re.compile('id:(\d),(\w{16})') 
        idstr_m = idstr_p.search(msg)
        csum_p  = re.compile('csumhere')
        csum_m  = csum_p.search(msg)
       
        # Server deals with id string 
        if idstr_m and self._type == 'srv':
          msgid = int(idstr_m.group(1))
          msgpw = str(idstr_m.group(2))
          # TODO: Open actual allowed clients list
          for client in self._cred:
            # Verify against 'id':'password' in clients list
            for id, pw in client.iteritems():
              id = int(id)
              pw = str(pw)
              if msgid == id and msgpw == pw:
                # connection verified ok
                # TODO:
                # Reply with DB table csum
                self._sock.send("csumhere")
                ret = True
                break
            if ret: break

        # Client deals with csum string 
        elif csum_m and self._type == 'rem':
          log.info(DT+"got csum message")
          ret = csum_m.group(0)
        else:
          log.error(DT+"should not happen")

      # no message 
      else:
        log.error(DT+"no verfiy msg")
    # Return
    return ret


