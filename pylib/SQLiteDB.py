#!/usr/bin/env python

import sqlite3
import sys
import logging as log

# Constants
DT        = 'db '
#DBPATH    = './db/data.db'
DBPATH    = '/home/jim/Montorhome/mh_project/app_srv/db/data.db'
INSERT    = "INSERT INTO sensor_readings" \
            "(type, value, name, date, raw_value)" \
            "values ('%s', %d, '%s', '%s', %d);"
SELECTALL = "select * from %s"
TABLES    = [ 'sensors', 'sensor_readings' ]

#
# Database functions
#
class SQLiteDB():

  def __init__(self, name="db", path=DBPATH, log=None):
    self._name   = name
    self._path   = path
    self._db     = None
    self._cur    = None
    self._tbls   = TABLES
    self._db     = None 

  #
  # Open Database at self._path
  #
  def open(self):
    ret = False
    # Check stuff
    if self._db is not None:
      log.warning(DT+'open db: already have db!')
    elif self._path is None:
      log.warning(DT+'open db: no db path!')
    else:
      # Open DB
      try:
        log.debug(DT+'%s - open database' % self._path)
        self._db = sqlite3.connect(self._path, timeout=5.0)
        if self._db: ret = True
      except Exception, e:
        log.debug(DT+"%s - failed to open db [e=%s]" % (self._path, e))
    return ret
 
  #
  # Close Database at self._path
  #
  def close(self):
    if self._db:
      log.debug(DT+"closing db %s" % self._path)
      self._db.close()

  #
  # Generate checksum for a table
  #
  def csum(self, tbls=None):
    
    # TODO: Undo this hack  
    sql = SELECTALL % TABLES[1]
    try :
      log.debug(DT+'execute [%s]' % sql)
      cur = self._db.cursor()
      cur.execute(sql)
      log.debug(DT+'commit')
      self._db.commit()
      log.debug(DT+'fetchone')
      cur.fetchone()[0]
    except Exception, e:
      log.error(DT+'Failed to get db csum [e=%s]' % e)
       

  #
  # Add reading (row) to Database table 'sensor_readings'
  #  
  # @type   TEXT
  # @value  INTEGER
  # @name   TEXT
  # @date   INTERGER
  # @reading_id INTEGER
  # raw_value   INTEGER
  def add_reading(self, type='', value=-1, name='', date='', reading_id='', raw_value=-1):
      
    sql = self.INSERT % (type, value, name, date, raw_value)

    try :
      log.debug(DT+'execute %s' % sql)
      cur = self._db.cursor()
      cur.execute(sql)
      log.debug(DT+'commit')
      self._db.commit()
#         self.log('fetchone')
#         cur.fetchone()[0]
    except Exception, e:
      log.debug(DT+'failed to add reading. e=%s' % e)
