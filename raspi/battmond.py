#!/usr/bin/env python


# Imports
import sys, time, json
from twisted.internet import reactor, defer, task
from twisted.protocols.basic import LineReceiver
from twisted.enterprise import adbapi
from twisted.internet.serialport import SerialPort, BaseSerialPort
# Custom imports
sys.path.insert(0, './pylib')
from DB import DB

# Globals (should be in config somewhere)
SER_PORT   = '/dev/ttyACM0'
BAUDRATE   = 9600
REQ_PERIOD = 15
LOGFILE    = './log/battmon.log'
DBPATH     = './db/data.db'

DT = 'batmon'
# Conversion factor
# data = raw_data/CON_FACTOR
CON_FACTOR = 66.28611153


#
# Log stuff
#
def log(msg):
  try:
    f = open(LOGFILE, "a")
  except Exception, e:
    sys.stderr.write("could not open logfile")
  tm_str = time.strftime('%y/%m/%d %H:%M:%S')
  log_str = "%s %s - %s\n" % (tm_str, DT, msg)
  f.write(log_str)
  f.close()

#
# Sensor data container
#
class sensorMsg:
  
  def __init__(self, msg_id=None, msg_data=None, msg_raw_data=None):
    self.id   = msg_id
    self.data = msg_data
    self.raw_data = msg_raw_data
    self.date = int(time.time())


#
# Protocol for the serial comms
#
class SerialProt(LineReceiver):

  def __init__(self):
    self.dbp    = DBPATH
    self._typ   = 'clnt'
    self.fp     = open(LOGFILE, 'a')
    self._db    = DB(self.dbp, self._typ, self.fp)

  def lineReceived(self, line):
    log("rx sensor data: %s" % line)
    rxcsum  = int(line.split(' ')[1], base=16)
    jsonstr = line.split(' ')[0] + ' '
    if not self.chk_csum(jsonstr, rxcsum):
      return
    msg = self._jsonDecode(jsonstr)
    d = defer.Deferred()
    d = self._db.insertdata(msg.id, msg.raw_data, msg.data, msg.date)


  #
  # Decode rx'd json string into sensorMsg object format.
  #
  def _jsonDecode(self, line):
    msg = sensorMsg()
    ret = False
    
    # {"sensor":[{"id":"0","val":"515"}]} 
    try:
      obj          = json.loads(line)
      sensor0      = obj['sensor'][0]
      msg.id       = int(sensor0['id'])
      msg.raw_data = int(sensor0['val'])
      msg.data     = int(int(msg.raw_data) / CON_FACTOR)
      
      log('json decode sensor0: data: %d, raw_data %d'
           % (msg.data, msg.raw_data))
      ret = msg
    except Exception, e:
      log("Error: can't decode sensor msg, e=%s" % e)

    return ret


  #
  # Check simple csum against data
  #
  def chk_csum(self, data, csum):
    ret = False
    data_csum = self._csum(data)
    if data_csum == csum:
      ret = True
    return ret

  #
  # Calculate simple csum
  #
  def _csum(self, data=None):
    ret = False
    if data:
      ret = 0;
      for c in data:
        ret += ord(c)
    return ret & 0xFF


if __name__ == '__main__':

  prot      = None
  ser_paths = ["/dev/ttyUSB%d", "/dev/ttyACM%d"]

  # send data to sensor (to elicit a reading response)
  def requestData():
    prot.writeSomeData('s')
 
  # loop through ttyACMx and ttyUSBx devices and try to open
  for i in range(0, 10):
    for path in ser_paths:
      ser_port = path % i
      try:
        log("Opening %s port" % ser_port)
        prot = SerialPort(SerialProt(), ser_port, reactor, BAUDRATE)
        lc = task.LoopingCall(requestData)
        lc.start(REQ_PERIOD)
      except Exception, e:
        log("failed to open serial port: %s" % SER_PORT)
        log("error: %s" % e)

  # Failed to connect to sensor
  # TODO: Don't bomb out, retry with back-offs
  log("Exiting")
  if prot == None:
    sys.exit(-1)

  reactor.run()
  
