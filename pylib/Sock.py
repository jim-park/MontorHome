#!/usr/bin/env python

import socket, sys, os
import logging as log
import time

# Constants - or config?
RETRYPERIOD = 15

#
# Socket Class to take care 
# of general functions
#
class Sock():
  DT = 'sock - '

  def __init__(self, sock=None, host=None, port=None, log=None):
    self._sock = sock 
    self._host = host
    self._port = port
    # passing a socket wins.
    if sock:
      self._sock = sock
    elif host and port:
      self.connect()
    else:
      log.error(DT+"not port or host provided. Failed.")

  
  #
  # Send data 
  #
  def send(self, data):
    if self._sock and len(data) > 0:
      try:
        self._sock.send("%s\r" % data)
        log.info(self.DT+"tx %d bytes: %s" % (len(data), data))
      except Exception, e:
        log.error(self.DT+"failed to send data. [e=%s]" % e)
    else:
      log.error(self.DT+"did not send data. No data or no socket")
 
  #
  # Recieve
  #
  def recv(self):
    log.info(self.DT+"recv")
    ret = False
    msg     = ''
    msg_len = 0 
    t = time.time()
    while True:
      char = None
      try:
        # log.info(self.DT+"recv(1)")
        char = self._sock.recv(1)
        # log.debug(self.DT+"char: %s" % char)
      except Exception, e:
        log.warning(self.DT+"recv err: [e=%s]" % e)
      if char is None:
        time.sleep(0.01)
        continue
      if char == '\r':
        break
      if (t < time.time() - 5):
        break
      msg = msg + char
      msg_len = len(msg)
    if msg_len > 0:
      log.debug(self.DT + "rx %d bytes: %s" % (msg_len, msg))
      ret = msg
    return ret
   

  #
  # Make a connection to app server
  #
  def connect(self):

    # check we got details to connect with
    if not (self._host or self._port):
      log.error(self.DT+"cannot connect. missing host and/or port")
      return False
    
    # check for existing socket
    if self._sock: 
      self._sock.close()
      self._sock = None

    # TODO: wrap the socket in ssl 
    # create socket obj
    cnt = 0
    while not self._sock and cnt < 8:
      try:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log.info(self.DT+"socket created")
        self._sock.connect((self._host, self._port))
        log.info(self.DT+"socket connected to %s %d" % (self._host, self._port))
        break
      except Exception, e:
        log.error(self.DT+"Failed to open socket to %s. [e=%s]" % (self._host, e))
        self._sock.close()
        self._sock = None

      # only get here if if we didn't connect
      log.warn("Retry connect in %d secs" % RETRYPERIOD)
      time.sleep(RETRYPERIOD)
      cnt = cnt + 1

  #
  # Close connection
  #
  def close(self):
    log.debug(self.DT+"Closing socket")
    if self._sock:
      self._sock.close()
      self._sock = None

