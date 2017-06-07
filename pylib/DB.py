#!/usr/bin/env python

# Imports
import os, sys, md5, time, sqlite3, thread
from threading import RLock

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor, defer, threads
from twisted.enterprise import adbapi
from twisted.python import log, threadpool

#
# DB class
#
class DB:
  SELECTALL     = "SELECT * FROM %s"
  SELALLORDBYID = "SELECT * FROM %s ORDER BY %s_id"
  INSERTDATA    = "INSERT INTO data (sensor_id, data, raw_data, date) "\
                  "values (%d, %0.2f, %d, %d)"
  INSERTDATAID  = "INSERT INTO data (data_id, sensor_id, data, "\
                  "raw_data, date) values (%d, %d, %0.2f, %d, %d)"
  INSERTEVENT   = "INSERT INTO event (tbl, rowid) values ('%s', %d)"
  DELETEEVENT   = "DELETE FROM event where rowid=%d and tbl=%s"

  #
  # Initialise
  #
  def __init__(self, dbpath, peer_type):
    self._peer   = peer_type
    self._dbpath = dbpath
    self._dbpool = adbapi.ConnectionPool("sqlite3", self._dbpath)
    self._dblock = RLock()
    
    self._dbpool.noisy = False #True - for noisy debug

  #
  # Execute deferred query in separate thread
  #
  def execute(self, sql):
    return threads.deferToThreadPool(reactor, self._dbpool.threadpool, self._execute, sql)

  #
  # Execute a given sql string (thread safe)
  #
  def _execute(self, sql):
    ret = None
    self._dblock.acquire()
    log.msg('exe SQL: %s' % sql)
    try:
      conn = self._dbpool.connect()
      cur  = conn.cursor()
      cur.execute(sql)
      conn.commit() 
      ret = cur.fetchall()
    except sqlite3.OperationalError, e:
      log.err("Error - Op Err, e: %s" % e)
    except Exception, e:
      log.err('Error executing sql. e:%s' % e)
    self._dbpool.disconnect(conn)
    self._dblock.release()
    return ret

  #
  # Select all (ordered) from a given table
  #
  def selectall(self, tbl):
    sql = self.SELALLORDBYID % (tbl, tbl)
    return self.execute(sql)

  #
  # TODO: finish this
  # Insert a new sensor into 'sensor' table
  #
  def insertsensor(self, type, name, sensor_id=None):
    pass

  #
  # Execute deferred INSERT in separate thread, and get insert id
  #
  def insertDataGetRowId(self, sdata):
    return threads.deferToThreadPool(reactor, self._dbpool.threadpool, 
                                     self._insertDataGetRowId, sdata)

  #
  # Insert data into 'data' table, get rowid (data_id),
  # add 'data_id' key and val to sdata
  #
  def _insertDataGetRowId(self, sdata):
    if self._peer != 'clnt': return None
    ret = True
    sql = self.INSERTDATA %\
         (sdata['id'], sdata['val'], sdata['raw_val'], sdata['time'])
    # Get lock and connection
    self._dblock.acquire()
    conn = self._dbpool.connect()
    
    try:
      cur = conn.cursor()
      log.msg('exe SQL: %s' % sql)
      cur.execute(sql) 
      conn.commit()
      sdata['data_id'] = cur.lastrowid
    except sqlite3.OperationalError, e:
      log.err("Error - Op Err, e: %s" % e)
    except Exception, e:
      log.err('Error executing sql. e:%s' % e)

    # Release lock and connection
    self._dbpool.disconnect(conn)
    self._dblock.release()

    return sdata


  #
  # Execute deferred INSERT in separate thread
  #
  def insertDataByRowId(self, sdata):
    return threads.deferToThreadPool(reactor, self._dbpool.threadpool, 
                                     self._insertDataByRowId, sdata)
    
  #
  # insert and don't return rowid
  #
  def _insertDataByRowId(self, sdata):
    if self._peer != 'srv': return None
    ret = True
    sql = self.INSERTDATAID %\
         (sdata['data_id'], sdata['id'], sdata['val'], sdata['raw_val'], sdata['time'])
    # Get lock and connection
    self._dblock.acquire()
    conn = self._dbpool.connect()
    
    try:
      cur = conn.cursor()
      log.msg('exe SQL: %s' % sql)
      cur.execute(sql) 
      conn.commit()
    except sqlite3.OperationalError, e:
      log.err("Error - Op Err, e: %s" % e)
    except Exception, e:
      log.err('Error executing sql. e:%s' % e)

    # Release lock and connection
    self._dbpool.disconnect(conn)
    self._dblock.release()

    return sdata

  #
  # Insert into 'event' table
  #
  def insertEvent(self, tbl, rowid):
    sql = self.INSERTEVENT % (tbl, rowid)
    return self._execute(sql)

  #
  # Make an md5 checksum from a selectall
  #
  def mkcsum(self, data, tbl):
    # Keep table name with it's csum, chaos otherwise
    return {tbl:md5.md5(str(data)).hexdigest()}

  #
  # Check a rxd checksum against local DB
  # expects a dict of {tblname:csum, ...:...,}
  #
  def cmptblcsum(self, tbl, rcsum):
    ret = False
    
    def cmp_csums(data, tbl, rcsum):
      ret = {tbl:False}
      if data[tbl] == rcsum:
        log.msg("tbl %s csum ok" % tbl)
        ret[tbl] = True
      else:
        log.msg("tbl %s csum doesn't match remote" % tbl)
      return ret

    d = defer.Deferred()
    d = self.selectall(tbl)
    d.addCallback(self.mkcsum, tbl)
    d.addCallback(cmp_csums, tbl, rcsum)
    
    return d


  #
  # Return dict of json strings with new tbl
  # rows as indicated in tbl event,
  # then remove row from event
  #
  def getevntrows(self):
    evnt_tbl = 'event'

    # returns dict where key=tblname, val=list of rowids
    # eg; tbls_data = {'sensor': [2], 'data': [1, 2, 3, 4, 5]}
    def fmtnewevrows(data):
      tbl_rowids = {}

      # create empty lists from tbl rows
      for r in data:
        tbl = str(r[1])
        tbl_rowids[tbl] = []

      # populate tbl row lists
      for r in data:
        tbl   = str(r[1])
        rowid = int(r[2])
        tbl_rowids[tbl].append(rowid)

      log.msg("tbl_rowid %s" % tbl_rowids)

      return tbl_rowids

    # Fetch a row from a given table with a given id
    def getrowbyid(tbl, rowid):
      sql = "SELECT * FROM %s WHERE %s_id = %d"\
            % (tbl, tbl, rowid)
      d = defer.Deferred()
      d = self.execute(sql)
     
      return d

    # input ('data') is dict of lists
    # eg {'sensor': [2], 'data': [1, 2, 3, 4, 5]}
    # return is dict of table row data
    # eg {'data':[(581, 0, 7.92, 525, 149), (583, 0, 8.39, 556, 149)], 'sensor':[2, 'a', 'batt1']}
    @inlineCallbacks
    def getevrowsbyid(tbl_rowids):
      tbl_data = {}
      log.msg("data: %s" % tbl_rowids)

      # initialise tbl_data dict of lists
      for tbl in tbl_rowids: tbl_data[tbl] = []

      for tbl in tbl_rowids:
        for rowid in tbl_rowids[tbl]:
          #self.log("tbl: %s, rowid: %s" % (tbl, rowid))
          d = yield getrowbyid(tbl, rowid)
          tbl_data[tbl].append(d[0])
      log.msg("tbl_data: %s" % tbl_data)

      returnValue(tbl_data)

    # select all from event
    d = defer.Deferred()
    d = self.selectall(evnt_tbl)
    d.addCallback(fmtnewevrows) 
    d.addCallback(getevrowsbyid)

    return d

