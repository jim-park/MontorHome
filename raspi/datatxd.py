#!/usr/bin/env python


####################################################################
#
# Daemon to read the db either when signaled or periodically
# Transmit any new readings from 'sensor_data' table to app server.
# Verify new readings were received by app server ok.
# 
####################################################################

import sqlite3, socket, sys, time
import logging as log
import socket
import fcntl, os 
# custom imports
sys.path.insert(0, './pylib')
from Daemon import Daemon
from Sock import Sock

#############
# Global constants

NAME       = 'datatxd'
LOGFILE    = './log/datatxd.log'
PIDFILE    = './run/datatxd.pid'
DBFILE     = './sqlite_db/data.db'
APPSRV     = 'comp1'
APPSRVPRT  = 4867
# TODO: deal with id string properly.
IDSTR     = 'id:0,iw9foj5ojv4dg2vd'
#IDSTR      = 'id:0,48hjgfd35pbor2sg'
IDSTRLEN   = len(IDSTR)


#
# Class to;
# Watch / periodically check for new db data.
# Transmit the data to the app server.
# Verify xmission was sucessful.
# 
class DataTXd(Daemon):

  def __init__(self):
    Daemon.__init__(self, pidfile=PIDFILE, name=NAME)
    # Daemon config
    self._name       = NAME
    # DB config 
    self._db_path    = DBFILE
    self._db         = None
    # logging 
    log.basicConfig(filename=LOGFILE,level=log.DEBUG, 
                    format='%(asctime)s.%(msecs)03d  %(message)s', 
                    datefmt='%m/%d/%Y %I:%M:%S')
    # Network config
    self._sock       = Sock(host=APPSRV, port=APPSRVPRT, log=log)

  #
  # Start
  #
  def _start(self):
    log.info("_starting")
    # Connect to the db
    #   Bail out if we can't
   
    # Connect to the app server
    #log.info("Connecting to app server")
    #self._sock.connect()
    # Send verfication
    log.info("Verifying ID with app server")
    if self._verify():
      log.info("Verified ID OK")
      # set to state dbinit
      self._state = 'dbinit'
    else:
      log.error("Failed to verify ID with app server")
      log.warning("Exiting")
      self.stop()
      sys.exit(0)

  #
  # Stop
  #
  def _stop(self):
    log.info("Stopping")
    if self._sock:
      self._sock.close()
      log.info("socket closed")
    log.info("Stopped")

  #
  # Main run loop
  #
  def _run(self):
    log.info("_running")
    # recieve db init (or don't)
    msg = self._sock.recv()
    
    if self._state == 'dbinit':
      self._dbinit(msg)
    # if dbinit False;
    #   compare last table ids
    #   van should be more recent than app srv.
    #   send missing values at ids
    #
    # set state idle 
    # listen for db changes;
    #   transmit if there are some
    # periodically request db csum
    time.sleep(25)

  #
  # Verify this client to the app server
  #
  def _verify(self):
    ret = False
    # send id string 
    self._sock.send(IDSTR)
    # positive respose is md5sum of db tables
    # 'sensors' + 'sensor_readings' 
    # check response OK?
    time.sleep(1)
    if self._sock.recv() == 'md5sumere':
      ret = True
    return ret

  #
  # DBInit, verify db csum and correct
  # client DB if necessary
  #
  def _dbinit(self, msg): pass
    

#
# Process entry point
#
if __name__ == "__main__":
  datatxd = DataTXd()

  if len(sys.argv) == 2:
    if 'start' == sys.argv[1]:
      datatxd.start()
    elif 'restart' == sys.argv[1]:
      datatxd.restart()
    elif 'stop' == sys.argv[1]:
      datatxd.stop()
    else:
      print "Unknown command"
      sys.exit(2)
    sys.exit(0)
  else:
    print "usage %s start|stop|restart" % sys.argv[0] 
    sys.exit(2)
