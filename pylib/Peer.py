#!/usr/bin/env python


# Imports
import sys, os, re, md5, time, json
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor, defer
from twisted.protocols.basic import LineReceiver
from twisted.enterprise import adbapi
# Custom imports
from DB import DB


# Dubious Globals
# TODO: move many of these into a file
# Srv
TABLES  = ['data', 'sensor']
CLIENTS = [ { "0" : "iw9foj5ojv4dg2vd" }]

# Clnt
#IDSTR   = '["init",{"id":"0","pw":"iw9foj5ojv4dg2vd"}]'
ID = "0"
PW = "iw9foj5ojv4dg2vd"


#
# Message container
#
class Msg:
  
  def __init__(self, msg_type=None, msg_data = dict()):
    self.type = msg_type
    self.data = msg_data



##########################################################
# Main class for dealing with a peer connection
##########################################################
class Peer(LineReceiver):
  INIT      = 'init'
  CSUM      = 'csum'
  ADD       = 'add'
  msg_types = [INIT, CSUM, ADD]

  def __init__(self, factory, typ='clnt', db= None, logfile=None):
    self.factory = factory
    self.fp      = logfile
    self._typ    = typ
    self._id     = 'X'
    self._verifd = False 
    self.dbp     = "./db/data.db"
    if db == None:
      self._db     = DB(self.dbp, self._typ, self.fp)
    else: 
      self._db   = db
  
  # 
  # Deal with a received line 
  #
  def lineReceived(self, line):
    msg = False
    
    self.log("rx: %s len %d" % (line, len(line)))
    msg = self._jsonDecode(line)

    # Check msg decoded ok
    if not msg: return

    # Check msg type allowed
    if msg.type not in self.msg_types:
      self.log('Error: bad msg type') 
      self.log('Aborting')
      return

    # Check client is verified (or is about to be)
    if not self._verifd and msg.type != self.INIT:
      self.log('Error: client not verfied') 
      self.log('Aborting')
      return
     
    # Deal with msg types 
    if msg.type == self.INIT: self._verify(msg)
    if msg.type == self.CSUM: self._rxcsum(msg)
    if msg.type == self.ADD:  self._rxadd(msg)

 
  #
  # Run when conn established
  #     
  def connectionMade(self):
    if self._typ == 'clnt':
      self.log("connection made")
      # TODO: Fix this, horrible
      data = {"id":ID,"pw":PW}
      self._txjson(self.INIT, data)
 
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
      self.log('json msg type: %s' % msg.type)
      for key, val in msg.data.iteritems():
        self.log('json msg data: %s : %s' % (key, val))
      ret = msg
    except Exception, e:
      self.log("Error: can't decode msg, e=%s" % e)

    return ret

  #
  # Receive db csum message
  #
  @inlineCallbacks
  def _rxcsum(self, msg):
    cb_res = []

    for tbl in msg.data:
      self.log('tbl: %s, rx csum: %s' % (tbl, msg.data[tbl]))
      d = defer.Deferred()
      d = yield self._db.cmptblcsum(tbl, msg.data[tbl])
      cb_res.append(d)

    for res in cb_res:
      for tbl in res:
        if not res[tbl]:
          self.log('tbl %s csum error' % tbl)
          # TODO: something about these misaligned tbls
          return
    self.log('All DB tables upto date')

  #
  # Receive add message
  #
  def _rxadd(self, msg):
    for tbl in msg.data:
      for row in msg.data[tbl]:
        self.log('add: %s : %s' % (tbl, row))
        if tbl == 'data':
          data_id = row[0]
          sens_id = row[1]
          value   = row[2]
          raw_val = row[3]
          date    = row[4]
          self._db.insertdata(sens_id, value, raw_val, date, data_id)
        elif tbl == 'sensor':
          # TODO: Finish this
          self._db.insertsensor(None, None, None)
        else:
          self.log("Error, should never happen, bad insert tbl")

  #
  # Send an 'add' message to the other end
  #
  def txadd(self, data):
    self.log("Peer.txadd")
    return self._txadd(data)

  #
  # Send add message to the other side
  #
  def _txadd(self, data):
    self.log("Peer._txadd")
    msg = Msg(type='add')
    jsondata = '{"id":"%d","sens_id":"%d","value":"%d",'\
               '"raw_value":"%d","data":"%d"}' %\
               (data[0], data[1], data[2], data[3], data[4])
    #data_id = row[0]
    #sens_id = row[1]
    #value   = row[2]
    #raw_val = row[3]
    #date    = row[4]
    self._txjson('add', jsondata)


  #
  # expects a list of tbl names
  #
  def txcsum(self, tbls=None):

    # create and send dict thus;
    # {'tbl0name':'tbl0csum', 'tbl1name':'tbl1csum'} and send it
    def sendcsum(data):
      csums = dict()
      for tbl_csum in data:
        csums.update(tbl_csum)
      # Send csum(s)
      self._txjson(self.CSUM, csums)
 
    # Funtion starts executing here
 
    # Default, sync table 'data'
    if tbls is None: tbls = ['data']
    
    # Setup callbacks from selectall for each table
    cb_refs = []
    for tbl in tbls:
      d = defer.Deferred()
      d = self._db.selectall(tbl)
      # when selectall finishes call mkcsum()
      d.addCallback(self._db.mkcsum, tbl)
      cb_refs.append(d)

    # Send csums when all selects return
    callbacks = defer.gatherResults(cb_refs)
    callbacks.addCallback(sendcsum)


  #
  # Set event in the 'event' table
  #
  def setEvent(self, tbl, rowid):
    self.log("inserting event, tbl: %s, row: %d" % (tbl, rowid))
    self._db.insertEvent(tbl, rowid)

  #
  # Get events from the 'event' table
  #
  def getEvent(self):
    self.log("getting event")
    newrows = yield self._db.getevntrows()

  #
  # Divert client or srv verification as necessary
  #
  def _verify(self, msg):
    if self._typ == 'clnt':
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

    # Success?
    if ret:
      self._id     = clid
      self._verifd = True
      self.log("client id %d verified ok" % self._id)
      # Send positive response to client
      self._txjson(self.INIT, {'verify':True})
    else:
      self.log("client failed verification, disconnected")
      # Send negative response to client
      self.transport.loseConnection()
    return ret

  #
  # Deal with srvs response to succesful verfication.
  #   If we haven't received a json string, we should
  #   have been disconnected by now anyway.
  # 
  def _verify_clnt(self, msg):
    # expecting;
    # msg.type == init
    # msg.data == {"verify":True}
    if msg.data['verify'] == True:
      self.log("srv response ok, verified")
      self.log("sending dbcsum")
      # TODO Fix this, TABLES orrid
      self.txcsum(tbls=TABLES)

  #
  # Send a json formatted string to the other end.
  #
  # expects; msg type, dict(msg data)
  def _txjson(self, msg_type, data):
    json_str = json.dumps([msg_type, data])
    self.log('tx: %s' % json_str)
    # TODO: Send a simple csum
    self.sendLine(json_str)
    
    
  # 
  # Log stuff to file
  #
  def log(self, msg):
    tag = self._typ
    if self._typ == 'srv':
      tag = 'clnt%s' % self._id
    if msg:
      self.fp.write("%s %s\n" % (tag, msg))
      self.fp.flush()


