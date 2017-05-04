#!/usr/bin/env python

# Imports
import os, sys, md5, time

from twisted.enterprise import adbapi
from twisted.internet import reactor, defer

#
# DB class
#
class DB:
  SELECTALL     = "SELECT * FROM %s"
  SELALLORDBYID = "SELECT * FROM %s ORDER BY %s_id"
  INSERTDATA    = "INSERT INTO data (sensor_id, data, raw_data, date) "\
                  "values (%d, %d, %d, %d)"
 
  # Initialisation 
  def __init__(self, dbpath, peer, logfileh=None):
    self._lfh    = logfileh
    self._peer   = peer
    self._dbpath = dbpath
    self._dbpool = adbapi.ConnectionPool("sqlite3", self._dbpath)

  # Execute a given sql string
  def _execute(self, sql):
    self.log('exe SQL: %s' % sql)
    return self._dbpool.runQuery(sql)

  # Select all (ordered) from a given table
  def selectall(self, tbl):
    #sql = "SELECT * FROM %s ORDER BY %s_id" % (tbl, tbl)
    sql = self.SELALLORDBYID % (tbl, tbl)
    return self._execute(sql)

  # Insert data into 'data' table
  def insertdata(self, sensor_id, data, raw_data, date):
    sql = self.INSERTDATA % ( sensor_id, data, raw_data, date)
    return self._execute(sql)
  
  # Make an md5 checksum from a selectall 
  def mkcsum(self, data, tbl):
    # Keep table name with it's csum, chaos otherwise
    return {tbl:md5.md5(str(data)).hexdigest()}

  # Check a rxd checksum against local DB
  # expects a dict of {tblname:csum, ...:...,}
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

    def ppprint(data):
      self.log("ppprint: %s" % data)
      return data

    #
    # returns dict where key=tblname, val=list of rowids
    # eg; tbls_data = {'sensor': [2], 'data': [1, 2, 3, 4, 5]}
    def fmtnewevrows(data):
      tbls_data = {}

      # create empty lists fro tbl rows
      for r in data:
        tbl = str(r[1])
        tbls_data[tbl] = []  

      # populate tbl row lists
      for r in data:
        tbl   = str(r[1])
        rowid = int(r[2])
        tbls_data[tbl].append(rowid)

      self.log("tbls_data %s" % tbls_data)    
      self.log("len(tbls_data) %d" % len(tbls_data))    

      return tbls_data  

    def getrowbyid(tbl, rowid):
      sql = "SELECT * FROM %s WHERE %s_id = %d"\
            % (tbl, tbl, rowid)
      d = defer.Deferred()
      d = self._execute(sql)
     
      return d 

    # input ('data') is dict of lists
    # eg {'sensor': [2], 'data': [1, 2, 3, 4, 5]}
    def getevrowsbyid(data):
      cb_refs = []
      for tbl in data:
        for rowid in data[tbl]:
          self.log("tbl: %s, rowid: %s" % (tbl, rowid))
          d = defer.Deferred()
          d = getrowbyid(tbl, rowid)
          d.addCallback(ppprint)
          cb_refs.append(d)
   # ["add":{"tblname": ("3", "1", "456", "654", "2017032723")}]

      cbs = defer.gatherResults(cb_refs)
      return cbs
        
    

    # select all from event
    d = defer.Deferred()
    d = self.selectall(evnt_tbl)
    d.addCallback(ppprint)
    d.addCallback(fmtnewevrows) 
    d.addCallback(getevrowsbyid)
    d.addCallback(ppprint)
    #d.addCallback(
    return d

   # loop through and get row data
   # from each table

   # format nicely and rtn



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

