#!/usr/bin/env python

import time, sys, json
from twisted.internet import reactor, task
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.protocol import ReconnectingClientFactory as RCFactory
from twisted.internet.serialport import SerialPort, BaseSerialPort
from twisted.protocols.basic import LineReceiver

# Globals
DT         = 'ser2tcp'  # Debug Tag
LOGFILE    = './log/'+DT+'.log'

SER_PATHS  = ['/dev/ttyUSB%d', '/dev/ttyACM%d']
BAUDRATE   = 9600 
REQ_PERIOD = 15         # request period (secs)

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
# Check simple csum against data
#
def chk_csum(data, csum):
  ret = False
  data_csum = simpl_csum(data)
  if data_csum == csum:
    ret = True
  return ret

#
# Calculate simple csum
#
def simpl_csum(data=None):
  ret = False
  if not data: return ret
  ret = 0;
  for c in data:
    ret += ord(c)
  return ret & 0xFF

#
# Protocol (but actually Factory) for the serial comms
#
class SerialFcty(LineReceiver):

  # Put rx'd data in the Q
  def lineReceived(self, line):
    log("ser rx: %s" % line)

    # Extract and check simple csum
    rxcsum  = int(line.split(' ')[1], base=16)
    jsonstr = line.split(' ')[0] + ' '
    if not chk_csum(jsonstr, rxcsum):
      log("Error: simple csum failed. Data ignored")
      return

    # Put timestamp on data
    jsonobj = json.loads(jsonstr)
    jsonobj['sensor'][0]['time'] = "%d" % int(time.time())
    jsontstr = json.dumps(jsonobj, separators=(',', ':'))

    # Append simple csum
    csum   = simpl_csum(jsontstr)
    txdata = jsontstr + ' %02X' % csum

    # Add to the queue for sending
    queue.append(txdata)
    if putter is not None:
      putter.sendData()
    else:
      log('local client not available, data buffered, len: %d' % len(queue))
      #log('data: %s' % txdata)

#
# TCP Client Protocol 
#
class txData(Protocol):
  
  def __init__(self):
    global putter
    putter = self

  def connectionMade(self):
    log("connected to local client")

  def connectionLost(self, reason):
    log("disconnected from local client")
    global putter
    putter = None

  def sendData(self):
    while len(queue) > 0:
      data = queue.pop()
      log("tcp tx: %s" % data)
      self.transport.write(data+'\n')


#
# TCP Reconnecting Client Factory
# Connects to local client
#
class txDataFactory(RCFactory):
  maxDelay = 1800  # 30 min

  def buildProtocol(self, addr):
    log("connected to local client %s" % addr)
    self.resetDelay()
    return txData()

  def startedConnecting(self, connector):
    log("attempting to connect to local client")

  def clientConnectionFailed(self, connector, reason):
    log('tcp connection to local client failed')
    #log('e=%s' % reason)
    RCFactory.clientConnectionFailed(self, connector, reason)

  def clientConnectionLost(self, connector, reason):
    log('tcp connection to local client lost')
    #log('e=%s' % reason)
    RCFactory.clientConnectionLost(self, connector, reason)


#
# Main entry point
#
def main():
  f  = txDataFactory()
  reactor.connectTCP('localhost', 8001, f)

  # send data to sensor (to elicit a reading response)
  # TODO: This should be somewhere else, surely!
  def reqSerData():
    log("requesting serial data")
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
          log('sensor on ser port %s connected ok' % ser_path)
          ser_conn = True
          break
        except Exception, e:
          log('serial port %s not available' % ser_path)
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
