#!/usr/bin/python

__author__ = "James Park"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"

import minimalmodbus
import serial
import time
import os

# Driver defaults
DEFAULT_SERIAL_PORT_NAME = "/dev/ttyUSB0"
DEFAULT_SERIAL_BAUD_RATE = 115200
DEFAULT_MODBUS_ADDRESS = 1

# Globals
DEV_INFO_BYTES = bytearray([0x01, 0x2b, 0x0e, 0x01, 0x00, 0x70, 0x77])  # Raw device information request


def get_high_byte(word):
    """Return the highest 8 bits of a 16-bit digit"""
    return (word & 0xFF00) >> 8


def get_low_byte(word):
    """Return the lowest 8 bits of a 16-bit digit"""
    return word & 0x00FF


class TracerBN(minimalmodbus.Instrument):
    """Instrument class for Tracer BN Series MPPT solar charger controller.

    Communicates via Modbus RTU protocol (via RS232 or RS485), using the *MinimalModbus* Python module.

    Args:
        * portname (str): port name
        * slaveaddress (int): slave address in the range 1 to 247

    Implemented with these function codes (in decimal):

    ==================  ====================
    Description         Modbus function code
    ==================  ====================
    Read registers      3
    Write registers     16
    ==================  ====================

    All register addresses were found in the document "ControllerProtocolV2.3.pdf" available
    from Jarkko Sonninens' execellent github page at https://github.com/kasbert/epsolar-tracer.

    """

    def __init__(self, portname=DEFAULT_SERIAL_PORT_NAME, slaveaddress=DEFAULT_MODBUS_ADDRESS):
        minimalmodbus.Instrument.__init__(self, portname, slaveaddress)
        self.debug = False
        self.serial.baudrate = DEFAULT_SERIAL_BAUD_RATE

        # Flush the serial buffer, before we begin
        try:
            while self.serial.read(1):
                continue
        except IOError:
            pass

    # Battery related
    def get_rated_batt_voltage(self):
        return self.read_register(int(0x3004), 2, 4)

    def get_batt_voltage(self):
        """Return the rated battery voltage"""
        return self.read_register(int(0x331A), 2, 4)

    def get_batt_current(self):
        """Return the instantaneous battery current"""
        return self.read_register(int(0x331B), 2, 4, signed=True)

    def get_batt_temp(self):
        """Return the temperature from the battery temperature sensor"""
        return self.read_register(int(0x311B), 2, 4, signed=True)

    def get_batt_rated_capacity(self):
        """Return the rated capacity of the battery"""
        return self.read_register(int(0x9001), 0, 3)

    def set_batt_rated_capacity(self, capacity):
        """Set the rated battery capacity of the battery"""
        return self.write_register(int(0x9001), capacity, 0)

    # Load related
    def get_load_current(self):
        """Return the instantaneous load current"""
        return self.read_register(int(0x310D), 2, 4)

    def get_load_power(self):
        """Return the instantaneous load power"""
        return self.read_register(int(0x310E), 2, 4)

    def get_load_voltage(self):
        """Return the instantaneous load voltage"""
        return self.read_register(int(0x310C), 2, 4)

    # PV related
    def get_pv_power(self):
        """Return the instantaneous PV power"""
        return self.read_register(int(0x3102), 2, 4)

    def get_pv_current(self):
        """Return the instantaneous PV input current"""
        return self.read_register(int(0x3101), 2, 4)

    def get_pv_voltage(self):
        """Return the instantaneous PV voltage"""
        return self.read_register(int(0x3100), 2, 4)

    # Controller Clock related
    def get_ctl_rtclock_sec(self):
        """Return the controller rtc seconds"""
        return get_low_byte(self.read_register(int(0x9013), 0, 3))

    def get_ctl_rtclock_min(self):
        """Return the controller rtc minutes"""
        return get_high_byte(self.read_register(int(0x9013), 0, 3))

    def get_ctl_rtclock_hour(self):
        """Return the controller rtc hours"""
        return get_low_byte(self.read_register(int(0x9014), 0, 3))

    def get_ctl_rtclock_day(self):
        """Return the controller rtc day of month"""
        return get_high_byte(self.read_register(int(0x9014), 0, 3))

    def get_ctl_rtclock_month(self):
        """Return the controller rtc month"""
        return get_low_byte(self.read_register(int(0x9015), 0, 3))

    def get_ctl_rtclock_year(self):
        """Return the controller rtc year"""
        return get_high_byte(self.read_register(int(0x9015), 0, 3))

    def get_ctl_rtclock_time(self):
        """Return the controller time as a time object"""
        t_str = "%s %s %s %s %s %s" % (self.get_ctl_rtclock_year(),
                                        self.get_ctl_rtclock_month(),
                                        self.get_ctl_rtclock_day(),
                                        self.get_ctl_rtclock_hour(),
                                        self.get_ctl_rtclock_min(),
                                        self.get_ctl_rtclock_sec())

        return time.strptime(t_str, "%y %m %d %H %M %S")

    def set_ctl_rtclock(self, year, mon, mday, hrs, mins, secs):
        """All time registers must be written at once
            year is a 2 digit number, not 4."""
        word0 = ((mins << 8) & 0xFF00) | secs  # mins : secs
        word1 = ((mday << 8) & 0xFF00) | hrs   # mday : hours
        word2 = ((year << 8) & 0xFF00) | mon   # year : mon
        return self.write_registers(int(0x9013), [word0, word1, word2])

    def set_ctl_rtclock_localtime(self):
        """Set the time on the tracer to localtime"""
        t = time.localtime()
        # We need a 2 digit year
        year = int(time.strftime("%y", t))
        return self.set_ctl_rtclock(year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)


# Interrogate serial ports for TracerBN device.
def find_serial_port():
    """Return the port path once the device is identified, otherwise raise an exception"""

    # This pythonic line of code creates an list of device paths (containing the
    # string "ttyUSB") from the /dev directory.  e.g ["/dev/ttyUSB0", "/dev/ttyUSB2"]
    ports_list = ["/dev/%s" % s for s in os.listdir('/dev') if "ttyUSB" in s]

    for port in ports_list:

        try:
            with serial.Serial(port, DEFAULT_SERIAL_BAUD_RATE) as s:
                s.write(DEV_INFO_BYTES)
                dev_info = s.read(int(62))  # read 62 bytes of device information returned

                if dev_info.find("Tracer"):
                    print "Found TracerBN on %s" % port
                    return port
                else:
                    print "A device is present at %s, but is not a TracerBN" % port

        except serial.SerialException:
            print "Failed to find device on port %s" % port

    # If we haven't found a device on a port by this point,
    # raise an exception. The device cannot be found.
    raise Exception('Failed to find TracerBN on any port')

