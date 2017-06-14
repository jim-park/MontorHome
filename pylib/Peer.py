#!/usr/bin/env python


# Imports
import sys, os, re, md5, time, json, thread
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor, defer
from twisted.protocols.basic import LineReceiver
from twisted.enterprise import adbapi
from twisted.python import log

# Custom imports
from DB import DB


# Dubious Globals
# TODO: move many of these into a file
# Srv details
TABLES  = ['data', 'sensor']
CLIENTS = [ { "0" : "iw9foj5ojv4dg2vd" }]

# Clnt credentials
ID = "0"
PW = "iw9foj5ojv4dg2vd"

# Define slave / master tags
SLVE = 'SLAVE'
MSTR = 'MASTER'

#
# Message container
#
class Msg:
  
  def __init__(self, msg_type=None, msg_data = dict()):
    self.type = msg_type
    self.data = msg_data

# Utility function to display the contents of a defered
def display(data):
  print("data display: %s" % data)
  return data

##########################################################
# Main class for dealing with a peer connection
# Peer to Peer DB sync class - has master / slave concept
##########################################################
class Peer(LineReceiver):
  INIT      = 'init'
  CSUM      = 'csum'
  ADD       = 'add'
  msg_types = [INIT, CSUM, ADD]

  def __init__(self, factory, typ=MSTR, db=None, logfile=None):
    self.factory = factory
    self._typ    = typ
    self._id     = 'X'
    self._verifd = False 
    self.dbp     = "./db/data.db"
    self.state   = 'vrfy'
    if db:
      self._db   = db
    else:
      self._db   = DB(self.dbp, self._typ)

    self.factory.protocol = self

  # 
  # Deal with a received line 
  #
  def lineReceived(self, line):
    msg = False
    
    log.msg("rx: %s len %d" % (line, len(line)), system='peer')
    msg = self._jsonDecode(line)

    # Check msg decoded ok
    if not msg: return

    # Check msg type allowed
    if msg.type not in self.msg_types:
      log.msg('Error: bad msg type', system='peer') 
      log.msg('Aborting', system='peer')
      return

    # Check client is verified (or is about to be)
    if not self._verifd and msg.type != self.INIT:
      log.msg('Error: client not verfied', system='peer') 
      log.msg('Aborting', system='peer')
      return
     
    # Deal with msg types 
    if msg.type == self.INIT and self.state == 'vrfy': self._verify(msg)
    if msg.type == self.CSUM and self.state == 'init': self._rxcsum(msg)
#     if msg.type == self.ADD  and self.state == 'idle': self._rxadd(msg)
    if msg.type == self.ADD: self._rxadd(msg)

 
  #
  # Run when conn established
  #     
  def connectionMade(self):
    if self._typ == MSTR:
      log.msg("connection made", system='peer')
      # TODO: Fix this, horrible
      data = {"id":ID,"pw":PW}
      self._txjson(data, self.INIT)
 
  #
  # Decode rx'd json string into Msg object format.
  #
  def _jsonDecode(self, line):
    msg = Msg()
    ret = False
    
    # ["init",{"id":"0", "pw":"iw9foj5ojv4dg2vd"}]
    try:
      obj      = json.loads(line)
      msg.type = obj[0]
      msg.data = obj[1]
#       log.msg('json msg type: %s' % msg.type, system='peer')
#       for key, val in msg.data.iteritems():
#         log.msg('json msg data: %s : %s' % (key, val), system='peer')
      ret = msg
    except Exception, e:
      log.msg("Error: can't decode msg, e=%s" % e, system='peer')

    return ret

  #
  # Receive db csum message and check all tables' csums against local db
  #
  def _rxcsum(self, msg):
    rowid = None
    log.msg('begin _rxcsum: %s' % (msg), system='peer')

    def cmpcsums(csum, rcsum):
      ret = False
      log.msg('%s == %s' % (csum, rcsum), system='peer')
      if csum == rcsum:
        ret = True
      return ret

    def sendselect(data, tbl):
      for row in data:
        rdata = dict()
        rdata['data_id'] = int(row[0])
        rdata['sens_id'] = int(row[1])
        rdata['val']     = row[2]     # round(float(row[3]))
        rdata['raw_val'] = int(row[3])
        rdata['time']    = int(row[4])
#         outobj = {tbl:rdata}
        self._txjson({tbl:rdata}, self.ADD)

    def tblsync(sync, tbl, rowid):
      if sync:
        self._state = 'idle'
        if self._typ == SLVE:
          self._txjson({tbl:"%s %s" % (True, rowid)}, self.CSUM)
          self._db.deltblbyid(tbl, rowid)
        else:
          d = self._db.selectgte(tbl, rowid + 1)
          d.addCallback(display)
          d.addCallback(sendselect, tbl)

        return sync

      else:
        rowid = int(int(rowid)/2)
        self._db.deltblbyid(tbl, rowid)
        self.txcsum(tbl, rowid)
        return sync

    # Function starts here
    for tbl in msg.data:
      rcsum = msg.data[tbl].split()[0]
      rowid = msg.data[tbl].split()[1]
      rowid = int(rowid)
      log.msg('tbl: %s, rcsum: %s rowid: %d' % (tbl, rcsum, rowid), system='peer')
      
      if rcsum == 'True' :
        # We have positive checksum confirmation
        log.msg('tbl: %s, synced ok to rowid: %d' % (tbl, rowid), system='peer')
        if self._typ == MSTR:  
          d = defer.Deferred()
          d = self._db.selectgte(tbl, rowid + 1)
          d.addCallback(display)
          d.addCallback(sendselect, tbl)
        break


      d = defer.Deferred()
      d = self._db.selectlte(tbl, rowid)
      d.addCallback(self._db.mkmd5csum)
      # If cmpcsums fails, we enter into dbsync.
      # halve the number of rows in the offending table
      # re-mkcsum, and see if the other end agrees
      d.addCallback(cmpcsums, rcsum)
      d.addCallback(display)
      d.addCallback(tblsync, tbl, rowid)
      


  #
  # Receive add message
  #
  def _rxadd(self, msg):
    for tbl in msg.data:
      
      # Debug output
      for field in msg.data[tbl]:
        log.msg('add tbl: %s - %s = %s' % (tbl, field, msg.data[tbl][field]), system='peer')

      if tbl == 'data':
        data = msg.data[tbl]
        try:
          self._db.insertDataByRowId(data)
        except Exception, e:
          log.err('didnt insert into tbl data', e)
      elif tbl == 'sensor':
        # TODO: Finish this
        self._db.insertSensorByRowId(None, None, None)
      else:
        log.err("Error, should never happen, bad insert tbl", system='peer')

  #
  # Send add message to the other side
  #
  def txadd(self, data, tbl):
    jsondata = {}
    jsondata[tbl] = data
    log.msg("Peer.txadd, data: %s" % jsondata, system='peer')
    self._txjson(jsondata, 'add')


  #
  # Make and send an md5csum for the table supplied
  # using data up to the rowid supplied
  #
  @inlineCallbacks
  def txcsum(self, tbl, rowid=None):

    log.msg("txcsum begin", system='peer')
    if rowid is None:
      # Get max rowid for table
      rowid = yield self._db.getmaxrowid(tbl)
      log.msg("rowid type: %s" % (type(rowid)))
      if type(rowid) == list: rowid = rowid[0][0]
      if rowid is None:       rowid = 0
    log.msg("tbl, rowid: %s, %s" % (tbl, rowid))

    d = defer.Deferred()
    d = self._db.selectlte(tbl, rowid)
    d.addCallback(self._db.mkmd5csum)
    d.addCallback(self._db.mktxcsumstr, tbl, rowid)
#     d.addCallback(display)
    d.addCallback(self._txjson, self.CSUM)

  #
  # Set event in the 'event' table
  #
  def setEvent(self, tbl, rowid):
    log.msg("inserting event, tbl: %s, row: %d" % (tbl, rowid), system='peer')
    self._db.insertEvent(tbl, rowid)

  #
  # Get events from the 'event' table
  #
  def getEvent(self):
    log.msg("getting event", system='peer')
    newrows = yield self._db.getevntrows()

  #
  # Divert client or srv verification as necessary
  #
  def _verify(self, msg):
    if self._typ == MSTR:
      self._verify_clnt(msg)
    else:
      self._verify_srv(msg)

  #
  # Verify client id string (id & pw)
  #
  def _verify_srv(self, msg):
    ret = False
    # verify ID string
    clid = int(msg.data['id'])
    clpw = str(msg.data['pw'])
    for client in CLIENTS:
      # Verify against 'id':'password' in clients list
      for id, pw in client.iteritems():
        if clid == int(id) and clpw == str(pw):
          # connection verified ok
          ret = True
          break
      if ret: break

    if ret:
      # Verification success
      self._id     = clid
      self._verifd = True
      self.state   = 'init'

      log.msg("client id %d verified ok" % self._id, system='peer')
      self._txjson({'verify':True}, self.INIT)
      
      # Send table csums to begin initialisation
      for tbl in TABLES:
        log.msg("call txcsum(%s)" % tbl, system='peer')
        self.txcsum(tbl)
        self.state = 'init'
    else:
      # Verification failure
      # Send negative response to client
      log.msg("client failed verification, disconnected", system='peer')
      self.transport.loseConnection()
    return ret

  #
  # Client deals with srvs response to successful verification.
  #   If we haven't received a json string, we should
  #   have been disconnected by now anyway.
  # 
  def _verify_clnt(self, msg):
    # expecting;
    # msg.type == init
    # msg.data == {"verify":True}
    if msg.data['verify'] == True:
      log.msg("verified with server ok", system='peer')
      self._verifd = True
      self.state   = 'init'

  #
  # Send a json formatted string to the other end.
  #
  # expects; msg type, dict(msg data)
  def _txjson(self, data, msg_type):
    # sanity check
    if msg_type not in self.msg_types:
      log.err("msg type: '%s' not allowed. msg not sent." % msg_type)
      return

    json_str = json.dumps([msg_type, data])
    log.msg('tx: %s' % json_str)
    # TODO: Send a simple csum
    self.sendLine(json_str)
    
    
