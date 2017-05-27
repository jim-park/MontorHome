#!/usr/bin/env python

# Imports
import os, sys, md5, time

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi

#
# DB class
#
class DB:
  SELECTALL     = "SELECT * FROM %s"
  SELALLORDBYID = "SELECT * FROM %s ORDER BY %s_id"
  INSERTDATA    = "INSERT INTO data (sensor_id, data, raw_data, date) "\
                  "values (%d, %0.2f, %d, %d)"
  INSERTDATAID  = "INSERT INTO data (data_id, sensor_id, data,"\
                  "raw_data, date) values (%d, %d, %0.2f, %d, %d)"
  INSERTEVENT   = "INSERT INTO event (tbl, rowid) values ('%s', %d)"
  DELETEEVENT   = "DELETE FROM event where rowid=%d and tbl=%s"

  #
  # Initialise
  #
  def __init__(self, dbpath, peer, logfileh=None):
    self._lfh    = logfileh
    self._peer   = peer
    self._dbpath = dbpath
    self._dbpool = adbapi.ConnectionPool("sqlite3", self._dbpath, cp_max=1)

  #
  # Execute a given sql string
  #
  def _execute(self, sql):
    ret = None
    self.log('exe SQL: %s' % sql)
    try:
      ret = self._dbpool.runQuery(sql)
    except Sqlite3.OperationalError, e:
      self.log("Error - Op Err, e: %s" % e)
    except Exception, e:
      self.log('Error executing sql. e:%s' % e)
    return ret

  #
  # Select all (ordered) from a given table
  #
  def selectall(self, tbl):
    sql = self.SELALLORDBYID % (tbl, tbl)
    return self._execute(sql)

  #
  # TODO: finish this
  # Insert a new sensor into 'sensor' table
  #
  def insertsensor(self, type, name, sensor_id=None):
    pass

  #
  # Insert data into 'data' table
  #
  def insertData(self, sensor_id, data, raw_data, date, data_id=None):
    if self._peer == 'clnt' and data_id == None:
      sql = self.INSERTDATA % ( sensor_id, data, raw_data, date)
    else:
      sql = self.INSERTDATAID % ( data_id, sensor_id, data, raw_data, date)
    return self._execute(sql)

  #
  # Insert into 'data' table and return data_id
  #
  def _insertdatagetrowid(self, txn, sdata):
    if self._peer != 'clnt': return None
    # insert the data
    sql = self.INSERTDATA %\
         (sdata['id'], sdata['val'], sdata['raw_val'], sdata['time'])
    self.log('exe SQL: %s' % sql)
    txn.execute(sql)
    # get last row id (data_id)
    sdata['data_id'] = txn.lastrowid
    return sdata

  #
  # Wrapper for _insertdatagetrowid()
  # (to get hold of txn object??)
  #
  def insertGetRowId(self, sdata):
    return self._dbpool.runInteraction(self._insertdatagetrowid, sdata)

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
        self.log("tbl %s csum ok" % tbl)
        ret[tbl] = True
      else:
        self.log("tbl %s csum doesn't match remote" % tbl)
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

      self.log("tbl_rowid %s" % tbl_rowids)

      return tbl_rowids

    # Fetch a row from a given table with a given id
    def getrowbyid(tbl, rowid):
      sql = "SELECT * FROM %s WHERE %s_id = %d"\
            % (tbl, tbl, rowid)
      d = defer.Deferred()
      d = self._execute(sql)
     
      return d

    # input ('data') is dict of lists
    # eg {'sensor': [2], 'data': [1, 2, 3, 4, 5]}
    # return is dict of table row data
    # eg {'data':[(581, 0, 7.92, 525, 149), (583, 0, 8.39, 556, 149)], 'sensor':[2, 'a', 'batt1']}
    @inlineCallbacks
    def getevrowsbyid(tbl_rowids):
      tbl_data = {}
      self.log("data: %s" % tbl_rowids)

      # initialise tbl_data dict of lists
      for tbl in tbl_rowids: tbl_data[tbl] = []

      for tbl in tbl_rowids:
        for rowid in tbl_rowids[tbl]:
          #self.log("tbl: %s, rowid: %s" % (tbl, rowid))
          d = yield getrowbyid(tbl, rowid)
          tbl_data[tbl].append(d[0])
      self.log("tbl_data: %s" % tbl_data)

      returnValue(tbl_data)

    # select all from event
    d = defer.Deferred()
    d = self.selectall(evnt_tbl)
    d.addCallback(fmtnewevrows) 
    d.addCallback(getevrowsbyid)

    return d



  # 
  # Log stuff to file
  #
  def log(self, msg):
    tag = self._peer+'db'
    if self._peer == 'srv':
      tag = 'clntdb'
    if msg:
      tm_str = time.strftime('%y/%m/%d %H:%M:%S')
      log_str = "%s %s - %s\n" % (tm_str, tag, msg)
      self._lfh.write(log_str)
      self._lfh.flush()

