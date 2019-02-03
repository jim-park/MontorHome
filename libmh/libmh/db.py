#!/usr/bin/env python

__author__ = "James Park"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"


# Imports
import os
import sqlite3
import hashlib as md5
from threading import RLock
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor, defer, threads
from twisted.enterprise import adbapi
from twisted.logger import Logger

# Local imports
# TODO: Fix this import
from libmh import MSTR


#
# DB class
#
class DB:
    # SELECTALL = "SELECT * FROM %s ORDER BY %s_id"
    SELECTLTE = "SELECT * FROM %s WHERE %s_id <= %s ORDER BY %s_id"
    SELECTGTE = "SELECT * FROM %s WHERE %s_id >= %s ORDER BY %s_id"
    SELECTMAX = "SELECT max(%s_id) FROM %s"
    INSERTDATA = "INSERT INTO data (sensor_id, data, raw_data, date) " \
                 "values (%d, %0.2f, %d, %d)"
    INSERTSENSOR = "INSERT INTO sensor (type, name) values ('%s', '%s')"
    INSERTDATAID = "INSERT INTO data (data_id, sensor_id, data, " \
                   "raw_data, date) values (%d, %d, %0.2f, %d, '%s')"
    INSERTSENSID = "INSERT INTO sensor (sensor_id, type, name) " \
                   "values ('%s', '%s', '%s' )"
    DELETEGTID = "DELETE FROM %s WHERE %s_id > %s"

    log = Logger()

    #
    # Initialise
    #
    def __init__(self, dbpath, peer_type):
        self._peer = peer_type
        self._dbpath = dbpath
        self._dbpool = None
        self._dblock = RLock()
        self.init()
        # self._dbpool = adbapi.ConnectionPool("sqlite3", self._dbpath)
        # self._dbpool.noisy = False  # True - for noisy debug

    #
    # Select all (ordered) from a given table
    #
    def selectall(self, tbl):
        sql = self.SELALLORDBYID % (tbl, tbl)
        return threads.deferToThreadPool(reactor, self._dbpool.threadpool,
                                         self._execute, sql
                                         )

    #
    # Select less than or equal to the given rowid
    #
    def selectlte(self, tbl, rowid):
        SELECTLTE = "SELECT %s FROM %s WHERE %s_id <= %s ORDER BY %s_id"
        if tbl == 'data':
            sql = SELECTLTE % ("data_id, sensor_id, data, raw_data, date", tbl, tbl, rowid, tbl)
        elif tbl == 'sensor':
            sql = SELECTLTE % ("sensor_id, type, name", tbl, tbl, rowid, tbl)
        return threads.deferToThreadPool(reactor, self._dbpool.threadpool,
                                         self._execute, sql
                                         )

    #
    # Select less than or equal to the given rowid
    #
    def selectgte(self, tbl, rowid):
        sql = self.SELECTGTE % (tbl, tbl, rowid, tbl)
        return threads.deferToThreadPool(reactor, self._dbpool.threadpool,
                                         self._execute, sql
                                         )

    #
    # Execute a given sql string (thread safe)
    #
    def _execute(self, sql):
        '''overriden by subclass'''
        pass

    #
    # INSERT into table 'data' and get insert id
    #
    @inlineCallbacks
    def insertdatagetid(self, sdata):
        self.log.debug("insertdatagetid called")
        sql = self.INSERTDATA % \
              (sdata['sens_id'], sdata['val'], sdata['raw_val'], sdata['time'])
        sdata['data_id'] = yield threads.deferToThreadPool(reactor, self._dbpool.threadpool,
                                                           self._insert, sql, getid=True)
        returnValue(sdata)

    #
    # INSERT into table 'sensor' and get insert id
    #
    @inlineCallbacks
    def insertsensorgetid(self, sdata):
        sql = self.INSERTSENSOR % \
              (sdata['type'], sdata['name'])
        sdata['sensor_id'] = yield threads.deferToThreadPool(reactor, self._dbpool.threadpool,
                                                             self._insert, sql, getid=True)
        returnValue(sdata)

    #
    # INSERT in to table 'data' including 'data_id'
    #
    def insertdatabyid(self, sdata):
        if self._peer == MSTR: return None
        # self.log.debug("insertdatabyid called")
        # 'YYYY-MM-DD HH:MM:SS[.fraction]'
        # sdata['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sdata['time']))
        # self.log.debug("datetime: %s" % sdata['time'])

        sql = self.INSERTDATAID % \
              (sdata['data_id'], sdata['sens_id'], sdata['val'], sdata['raw_val'], sdata['time'])

        return threads.deferToThreadPool(reactor, self._dbpool.threadpool,
                                         self._insert, sql, getid=False)

    #
    # INSERT in to table 'sensor' including 'sensor_id'
    #
    def insertsensorbyid(self, sdata):
        if self._peer == MSTR: return None
        sql = INSERTSENSID % \
              (sdata['sensor_id'], sdata['type'], sdata['name'])
        return threads.deferToThreadPool(reactor, self._dbpool.threadpool,
                                         self._insert, sql, getid=False)

    #
    # Insert data into table, return insert rowid if flagged
    #
    def _insert(self, sql, getid=False):
        ret = True
        # Get lock and connection
        self._dblock.acquire()
        conn = self._dbpool.connect()
        try:
            cur = conn.cursor()
            self.log.debug('exe: {sql}', sql=sql, system='db')
            cur.execute(sql)
            conn.commit()
            if getid:
                ret = cur.lastrowid
        except sqlite3.OperationalError, e:
            self.log.error("Error - Op Err, e: %s" % e)
            ret = False
        except Exception, e:
            self.log.error('Error executing sql. e:%s' % e)
            ret = False

        # Release lock and connection
        self._dbpool.disconnect(conn)
        self._dblock.release()

        return ret

    #
    # Delete data greater than 'rowid' from table data
    #
    def deltblgtid(self, tbl, rowid):
        if self._peer == MSTR:
            self.log.debug('wont delete db data from master. tbl: {tbl}', tbl=tbl, system='db')
            return
        sql = self.DELETEGTID % (tbl, tbl, rowid)
        return threads.deferToThreadPool(reactor, self._dbpool.threadpool,
                                         self._execute, sql
                                         )

    #
    # Get the max rowid for the table supplied
    #
    def getmaxrowid(self, tbl):
        sql = self.SELECTMAX % (tbl, tbl)
        return threads.deferToThreadPool(reactor, self._dbpool.threadpool,
                                         self._execute, sql
                                         )

    #
    # Concatenate a csum and rowid, leaving a space in-between
    #
    # TODO: Move this out of here, it's not a DB function
    def mktxcsumstr(self, csum, tbl, rowid):
        if rowid == None: rowid = 0
        return {tbl: '%s %s' % (csum, rowid)}

    #
    # Make an md5 checksum from select data and append rowid
    #
    # TODO: Move this out of here, it's not a DB function
    def mkmd5csum(self, data):
        # log.debug(data, system='db')
        return md5.md5(str(data)).hexdigest()

    #
    # Make an md5csum for the table supplied
    # using data up to the rowid supplied
    #
    # TODO: Move this out of here, it's not a DB function
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


#
# Sqlite3 superclass
#
class SQLite3DB(DB):
    log = Logger()

    def __init__(self, dbpath, peer_type):
        DB.__init__(self, dbpath, peer_type)
        self._dbpool = adbapi.ConnectionPool("sqlite3", self._dbpath)
        self._dbpool.noisy = False  # True - for noisy debug

    #
    # Sqlite3 DB init
    #
    def init(self):
        # Check if db exists, if not create it
        if not os.path.exists(self._dbpath):
            pass

    #
    # Execute a given sql string (thread safe)
    #
    def _execute(self, sql):
        ret = None
        conn = None
        self._dblock.acquire()
        self.log.debug("exe: {sql}", sql=sql, system="sql3")
        try:
            conn = self._dbpool.connect()
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            ret = cur.fetchall()
        except sqlite3.OperationalError, e:
            self.log.error("Error - OpErr, e:{e}", e=e, system='sql3')
        except Exception, e:
            self.log.error('Error - unknown exception executing sql. e:{e}', e=e, system='sql3')
        if conn is not None:
            self._dbpool.disconnect(conn)
        self._dblock.release()
        if ret:
            return ret


#
# MySQL superclass
#
class MySQLDB(DB):
    log = Logger()

    def __init__(self, dbpath, peer_type):
        DB.__init__(self, dbpath, peer_type)
        self._dbpool = adbapi.ConnectionPool("mysql.connector", user='mh_db_user',
                                                                password='app_srv0HFY',
                                                                host='127.0.0.1',
                                                                database='mh_data')

    #
    # Placeholder for DB init
    #
    def init(self):
        pass

    #
    # Execute a given sql string (thread safe)
    #
    def _execute(self, sql):
        ret = None
        cur = None
        self._dblock.acquire()
        self.log.debug('exe: {sql}', sql=sql, system='mysql')
        try:
            conn = self._dbpool.connect()
            cur = conn.cursor()
            cur.execute(sql)
            ret = cur.fetchall()
            conn.commit()
        except Exception, e:
            self.log.error('Error - unknown exception executing sql. e={e}', e=e, system='mysql')
        if cur is not None:
            cur.close()
        self._dbpool.disconnect(conn)
        self._dblock.release()
        return ret
