#!/usr/bin/env python

import time, sys, json
from twisted.internet import reactor, task
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.serialport import SerialPort, BaseSerialPort
from twisted.protocols.basic import LineReceiver

# Globals
DT         = 'ser2tcp'  # Debug Tag
LOGFILE    = './log/'+DT+'.log'

SER_PATHS  = ['/dev/ttyUSB%d', '/dev/ttyACM%d']
BAUDRATE   = 9600 
REQ_PERIOD = 60         # request period (secs)

queue = []
putter = None

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
  f.flush()
  f.close()

#
# Protocol (but actually Factory) for the serial comms
#
class SerialFcty(LineReceiver):

  #def __init__(self):
  #  # TODO: this is horrid. 
  #  self.fp     = open(LOGFILE, 'a')
  #  log("SerialFcty init'd")

  # Put rx'd data in the Q
  def lineReceived(self, line):
    log("rx: %s" % line)
    queue.append(line)
    if putter is not None:
      putter.sendData()
    else:
      log('tcp client not available, data buffered')

#
# TCP Client Protocol 
#
class txData(Protocol):
  
  def __init__(self):
    global putter
    putter = self

  def connectionMade(self):
    log("Connected to local client")

  def connectionLost(self, reason):
    log("Disconnected from local client")
    global putter
    putter = None

  def sendData(self):
    while len(queue) > 0:
      data = queue.pop()
      log("tx: %s" % data)
      self.transport.write(data+'\n')


#
# TCP Client Factory
#
class txDataFactory(ReconnectingClientFactory):
  initialDelay = 10
  factor       = 1.5
  maxDelay     = 600

  def buildProtocol(self, addr):
    self.resetDelay()
    return txData()

  def clientConnectionFailed(self, connector, reason):
    log('TCP connection to client failed e=%s' % reason)
    self.retry(connector)

  def clientConnectionLost(self, connector, reason):
    log('TCP connection to client lost e=%s' % reason)
    self.retry(connector)


#
# Main entry point
#
def main():
  f  = txDataFactory()
  reactor.connectTCP('localhost', 8001, f)

  # send data to sensor (to elicit a reading response)
  # TODO: This should be somewhere else, surely!
  def reqSerData():
    log("request serial data")
    f.writeSomeData('s')
  
  # Loop through ttyACMx and ttyUSBx devices and try to open
  while True:
    # TODO, timeout of infinite loop
    ser_conn = False
    for i in range(0, 10):
      for p in SER_PATHS:
        ser_path = p % i
        try:
          f = SerialPort(SerialFcty(), ser_path, reactor, BAUDRATE)
          log('Sensor on ser port %s connected ok' % ser_path)
          ser_conn = True
          break
        except Exception, e:
          log('Ser port %s not available' % ser_path)
      if ser_conn: break
    if ser_conn: break
    time.sleep(10)

  # Request serial data every REQ_PERIOD secs (60)
  lc = task.LoopingCall(reqSerData)
  lc.start(REQ_PERIOD)

  # No point running reactor unless serial connection is made.
  reactor.run()

 
#
# Call main()
#
if __name__ == '__main__': main()
