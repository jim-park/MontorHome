#!/usr/bin/env python

import sys, datetime, serial, time, json
from StringIO import StringIO
from time import sleep
from serial import SerialException
import sqlite3
import logging as log
# custom imports
sys.path.insert(0, './pylib')
from Daemon import Daemon

LOGFILE = './log/battmond.log'
PIDFILE = './run/battmond.pid'
DBFILE  = './db/data.db'

def logtime():
  from time import strftime
  return strftime("%Y-%m-%d %H:%M:%S")


class SQLiteDB():
    INSERT = "INSERT INTO sensor_readings (type, value, name, date, raw_value) " \
                                   "values ('%s', %d, '%s', '%s', %d);"

    def __init__(self, name="SQLite", path=DBFILE):
      self._name   = name
      self._path   = path
      self._db     = None
      self._cur    = None
      self._db     = self._open()  

    def log(self, msg=None):
      if self._log_fh and msg:
        self._log_fh.write("%s - %s\n" % (logtime(), msg))
        
    #
    # Open Database at self._path
    #
    def _open(self):
      ret = None
      if self._db: return
      if self._path:
        try:
          self._path = DBFILE
          self.log('%s - open database' % self._path)
          ret = sqlite3.connect(self._path, timeout=5.0)
        except Exception, e:
          self.log("%s - failed to open db [e=%s]" % (self._path, e))
      return ret
 
    #
    # Close Database at self._path
    #
    def close(self):
      if self._db:
        self.log("closing db %s" % self._path)
        self._db.close()
 
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
        self.log('execute %s' % sql)
        cur = self._db.cursor()
        cur.execute(sql)
        self.log('commit')
        self._db.commit()
#         self.log('fetchone')
#         cur.fetchone()[0]
      except Exception, e:
        self.log('failed to add reading. e=%s' % e)


class BattMond(Daemon):
  #CON_FACTOR = 68.2666
  CON_FACTOR = 66.28611153

  def __init__(self, name='battmond'):
    Daemon.__init__(self, PIDFILE, name=name)
    self._name       = name
    self._smp_period = 20 
    self._smp_timer  = 0
    
    self._db_path    = DBFILE
    self._db         = None

    # serial port settings
    self._ser        = None
    self._baud_rate  = 9600
    
    # setup logging
    log.basicConfig(filename=LOGFILE,level=log.DEBUG, 
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s', 
                    datefmt='%m/%d/%Y %H:%M:%S')

  #
  # _Start
  # 
  def _start(self):
    log.info("start") 

    # Open serial port
    self._open_serial()


  #
  # _Stop
  # 
  def _stop(self):
    log.info("Stopping")
    

  #
  # Run
  # 
  def _run(self):
    log.info("running")
    
    while self._ser is None:
      log.error("Serial port not connected")
      log.error("Attempt to connect to serial port in 1 min")
      time.sleep(60)
      self._open_serial()
       
    # log.info("%s - time: %s > %s \n" % (logtime(), time.time(), (self._sample_per+self._timer)))
    if (time.time() > (self._smp_period + self._smp_timer)):
      data = self.get_data()
      out_string =  "%s : %s" % (logtime(), data)
      self._dfh.write(out_string)
      sensor_data = self._decode(data)
      
      if sensor_data:
        voltage    = float(int(sensor_data[0]['val'])/self.CON_FACTOR)
        out_string =  "%s : %d : %0.2f V\n" % (logtime(), int(sensor_data[0]['val']), voltage)
        self._dfh.write(out_string)
        self._add_reading(voltage, sensor_data[0])
        self._smp_timer = time.time()


  #
  # Verify and decode json data 
  #
  def _decode(self, data = None):
    
    # split csum and data
    if data:
      rxcsum  = int(data.split(' ')[1], base=16)
      jsonstr = data.split(' ')[0] + ' '
      csum = self._csum(jsonstr)
      
#       self._lfh.write('%s - rxcsum is: %X \n' % (logtime(), rxcsum))
#       self._lfh.write('%s - csum is: %X \n' % (logtime(), csum))
      
      # verify csum
      if csum == rxcsum:
        # decode data
        # This is the format to use, much better
        # {"id":"0","sensors":[{"id":"0", "type":"a", "val":"582"}, {"id":"1", "type":"d", "val":"542"}]}
        io = StringIO(data.split(' ')[0])
        sample       = json.load(io)
        controllerid = sample['id']
        sensorid     = sample['sensors'][0]['id']
        sensortype   = sample['sensors'][0]['type']
        sensorval    = sample['sensors'][0]['val']

        self._lfh.write('%s - controller id %s \n' % (logtime(), controllerid))
        self._lfh.write('%s - sensor id %s \n' % (logtime(), sensorid))
        self._lfh.write('%s - sensor type %s \n' % (logtime(), sensortype))
        return sample['sensors']
      else:
        self._lfh.write('%s - bad csum [%X] for data: %s' % (logtime(), csum, data))
        return False
        
    
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

  #
  # Get data from serial port
  #
  def get_data(self):
    ret = None
    # Write to serial port - request sample
    try:
      self._ser.write("s")
    except SerialException, e:
      self._lfh.write("%s - error writing to serial port \n" % logtime())
      self._lfh.write("%s - error: %s \n" % (logtime(), e))
      self._ser.close()
      self._ser = None
      return ret    

    # Read raw sample from serial port
    try:
      ret = self._ser.readline()
    except SerialException, e:
      self._lfh.write("%s - error reading from serial port \n" % logtime())
      self._lfh.write("%s - error: %s \n" % (logtime(), e))
      self._ser.close()
      self._ser = None  
      return None
 
    return ret


  #
  # Open serial port
  # 
  def _open_serial(self):

    if self._ser: 
      self._ser.close()
      self._ser = None
    
    # search serial ports ttyACMx and ttyUSBx (for x<10)
    ser_paths = ["/dev/ttyUSB%d", "/dev/ttyACM%d"]
    for i in range(0, 10):
      for path in ser_paths:
        ser_port = path % i 
        try:
          log.info("Trying serial port, %s" % ser_port)
          self._ser = serial.Serial(ser_port, self._baud_rate) 
        except OSError:
          pass
        except Exception, e:
          log.error("Exception: [e=%s]" % e)
        if self._ser: break
    
    if self._ser:
      log.info("Opened serial port %s ok" % ser_port)
    else:
     log.error("error connecting to serial port.")


  #
  # add reading to sqlite db
  #
  def _add_reading(self, value, sensor_data=None, ):
    if not self._db:
      self._db = SQLiteDB(path=self._db_path, log_fh=self._lfh)
    
    name = 'batt2'
    type = sensor_data['type']
    date = time.time()
    self._db.add_reading(type=type, value=float(value), name=name, date=date, raw_value=int(sensor_data['val']))
    
    


if __name__ == "__main__":
  battmond = BattMond()
  if len(sys.argv) == 2:
    if 'start' == sys.argv[1]:
      battmond.start()
    elif 'restart' == sys.argv[1]:
      battmond.restart()
    elif 'stop' == sys.argv[1]:
      battmond.stop()
    else:
      print "Unknown command"
      sys.exit(2)
    sys.exit(0)
  else:
    print "usage %s start|stop|restart" % sys.argv[0] 
    sys.exit(2)
