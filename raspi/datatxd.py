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
from Prot import Prot

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
class DataTXd(Prot):

  def __init__(self, log):
    #Daemon.__init__(self, pidfile=PIDFILE, name=NAME)
    Prot.__init__(self, 'rem', name=NAME, srv=APPSRV, prt=APPSRVPRT, log=log, cred=IDSTR)


#
# Process entry point
#
if __name__ == "__main__":
  log.basicConfig(filename=LOGFILE,level=log.DEBUG, 
                  format='%(asctime)s.%(msecs)03d  %(message)s', 
                  datefmt='%m/%d/%Y %I:%M:%S')
  datatxd = DataTXd(log)

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
