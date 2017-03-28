#!/usr/bin/env python

import sqlite3
import sys
import logging as log
import json
import md5

# Constants
DT        = 'db '
#DBPATH    = './db/data.db'
DBPATH    = '/home/jim/Montorhome/mh_project/app_srv/db/data.db'
INSERT    = "INSERT INTO sensor_readings" \
            "(type, value, name, date, raw_value)" \
            "values ('%s', %d, '%s', '%s', %d);"
SELECTALL = "SELECT * FROM %s ORDER BY %s"
TABLES    = [ 'sensor', 'data' ]

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
  def _tblcsum(self, tbl=None):
    ret = False
    if not tbl:
      log.error(DT+"can't do tblcsum, no tbl specified") 
      return ret
    #sql = SELECTALL + 'ORDER BY %s_id' % (tbl, tbl)
    sql = 'SELECT * from %s ORDER BY %s_id' % (tbl, tbl)
    try :
      cur = self._db.cursor()
      log.debug(DT+'execute [%s]' % sql)
      cur.execute(sql)
      # TODO, limit select, not selectall.
      data = cur.fetchall()
      # log.debug(DT+'fetched: %s' % data)
      ret = self._csum(str(data)).hexdigest()
    except Exception, e:
      log.error(DT+'Failed to get db csum [e=%s]' % e)
       
    return  ret
  #
  # Generate Json formtted table csum message
  #
  def csummsg(self, table=None):
    # { "csum": { "sensors" : "0xcsum", "sensor_data" : "0xcsum"} }
    ret      = False
    tblcsums = []
    JCSUM    = '{"csum":{%s}}'
    flg      = False
    jstr     = ''
    if not table:
      # If not tbl specified, do them all
      # TODO: Undo this hack
      table = TABLES
    
    for t in table:
      if flg: jstr = jstr + ','
      csum = self._tblcsum(t)
      tblcsums.append(csum)
      jstr = jstr + '"%s":"%s"' % (t, csum)
      # log.info(DT+"csum: %s: %s" % (t, csum))
      flg = True
    if jstr != '': ret = JCSUM % jstr
    log.info(DT+"jstr: %s" % (ret))
    return ret

  #
  # Calculate simple csum
  #
  def _csum(self, data=None):
    ret = False
    if data:
      ret = md5.md5(str(data))
    return ret
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
