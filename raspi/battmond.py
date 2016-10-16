#!/usr/bin/env python

import sys, datetime, serial, time
from Daemon import Daemon
from time import sleep
from serial import SerialException

def logtime():
  from time import strftime
  return strftime("%Y-%m-%d %H:%M:%S")

class BattMond(Daemon):
  #CON_FACTOR = 68.2666
  CON_FACTOR = 66.28611153

  def __init__(self, pidfile, name="battmond"):
    Daemon.__init__(self, pidfile, name=name)
    self._name       = name
    self._log_file   = "/home/jim/Montorhome/raspi/run/test.log"
    self._lfh        = None
    self._data_file  = "/home/jim/Montorhome/raspi/run/data.log"
    self._dfh        = None
    self._smp_period = 20 
    self._smp_timer  = 0

    # serial port settings
    self._ser        = None
    self._baud_rate  = 9600


  #
  # _Start
  # 
  def _start(self):
    print "%s - _start()" % self

    # Open files
    try:
      self._lfh = open(self._log_file, "a", 0)
      self._dfh = open(self._data_file, "a", 0)
    except Exception, e:
      sys.stderr.write("%s - Failed to open a log file. [e=%s] \n" % (logtime(), e))
      if self._lfh:
        lf.write("%s - Failed to open a log file. [e=%s] \n" % (logtime(), e))
      # stop
      self.stop()
    # opened ok? 
    if self._lfh and self._dfh:
      self._lfh.write("%s - Opened log files ok \n" % logtime())

    # Open serial port
    self._open_serial()


  #
  # _Stop
  # 
  def _stop(self):
    self._lfh.write("%s - Stopping \n" % logtime())
    
    # Close open file handles
    if self._lfh: self._lfh.close()
    if self._dfh: self._dfh.close()
    # Close serial port fh
    if self._ser: self._ser.close()

  #
  # Run
  # 
  def _run(self):
    
    if not self._ser:
      self._lfh.write("%s - try to reconnect to serial port \n" % logtime())
      self._open_serial()
       
    # self._lfh.write("%s - time: %s > %s \n" % (logtime(), time.time(), (self._sample_per+self._timer)))
    if (time.time() > (self._smp_period + self._smp_timer)):
      data = self.get_data()

      if data:
        voltage    = float(int(data)/self.CON_FACTOR)
        out_string =  "%s : %d : %0.2f V\n" % (logtime(), int(data), voltage)
        self._dfh.write(out_string)
        self._smp_timer = time.time()
 

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
          self._lfh.write("%s - Trying serial port, %s \n" % (logtime(), ser_port))
          self._ser = serial.Serial(ser_port, self._baud_rate) 
        except Exception, e:
          self._lfh.write("%s - error connecting to %s \nerror: %s \n" % (logtime(), ser_port, e))
        if self._ser: break
      if self._ser: 
        self._lfh.write("%s - Opened serial port, %s ok \n" % (logtime(), ser_port))
        break


if __name__ == "__main__":
  battmond = BattMond(pidfile='/home/jim/Montorhome/raspi/run/battmon.pid')
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
