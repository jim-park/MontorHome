#!/usr/bin/env python

# Imports
import os, sys, md5, time, sqlite3, thread
from threading import RLock
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor, defer, threads
from twisted.enterprise import adbapi
from twisted.python import log, threadpool

# Local imports
#from Peer import SLVE, MSTR
# Because the above import don't work......
# Define slave / master tags
SLVE = 'SLAVE'
MSTR = 'MASTER'


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
    return threads.deferToThreadPool( reactor, self._dbpool.threadpool,
                                       self._execute, sql
                                     )

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
      log.err("Error - OpErr, e: %s" % e)
    except Exception, e:
      log.err('Error - unknown exception executing sql. e:%s' % e)
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
  # Select less than or equal to the given rowid
  #
  def selectlte(self, tbl, rowid):
    sql = 'SELECT * FROM %s WHERE %s_id <= %s ORDER BY %s_id' %\
           (tbl, tbl, rowid, tbl)
    return self.execute(sql)

  #
  # Select less than or equal to the given rowid
  #
  def selectgte(self, tbl, rowid):
    sql = 'SELECT * FROM %s WHERE %s_id >= %s ORDER BY %s_id' %\
           (tbl, tbl, rowid, tbl)
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
                                     self._insertdatagetid, sdata)

  #
  # Insert data into 'data' table, get rowid (data_id),
  # add 'data_id' key and val to sdata
  #
  def _insertdatagetid(self, sdata):
    if self._peer != MSTR: return None
    ret = True
    sql = self.INSERTDATA %\
         (sdata['sens_id'], sdata['val'], sdata['raw_val'], sdata['time'])
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
                                     self._insertdatabyid, sdata)

  #
  # insert and don't return rowid
  #
  def _insertdatabyid(self, sdata):
    if self._peer != SLVE: return None
    ret = True
    sql = self.INSERTDATAID %\
         (sdata['data_id'], sdata['sens_id'], sdata['val'], sdata['raw_val'], sdata['time'])
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
  # Delete data greater than 'rowid' from table data
  #
  def deltblbyid(self, tbl, rowid):
    if self._peer == MSTR:
      log.msg('wont delete db data from master')
      return
    sql = 'DELETE FROM %s WHERE %s_id > %s' % (tbl, tbl, rowid)
    return self.execute(sql)

  #
  # Insert into 'event' table
  #
  def insertEvent(self, tbl, rowid):
    sql = self.INSERTEVENT % (tbl, rowid)
    return self._execute(sql)

  #
  # Get the max rowid for the table supplied
  #
  def getmaxrowid(self, tbl):
    sql = 'select max(%s_id) from %s' % (tbl, tbl)
    return self.execute(sql)

  #
  # Concatenate a csum and rowid, leaving a space in-between
  #
  def mktxcsumstr(self, csum, tbl, rowid):
    if rowid == None: rowid = 0
    return {tbl: '%s %s' % (csum, rowid)}

  #
  # Make an md5 checksum from select data and append rowid
  #
  def mkmd5csum(self, data):
    return md5.md5(str(data)).hexdigest()

  #
  # Make an md5csum for the table supplied
  # using data up to the rowid supplied
  #
  def mktblcsum(self, tbl, rowid=None):

    if rowid is None:
      # Get max rowid for table
      rowid = yield getmaxrowid(tbl)
      rowid = rowid[0][0]
      print("rowid: %s" % rowid)

    def display(data):
      print("db display: %s" % data)
      return data

    d = defer.Deferred()
    d = self.selectlte(tbl, rowid)
    d.addCallback(self.mkmd5csum)
    d.addCallback(self.mktxcsumstr, tbl, rowid)
    d.addCallback(display)

  '''
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

    '''
