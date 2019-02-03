#!/usr/bin/python

__author__ = "James Park"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"

import minimalmodbus

# Driver defaults
SERIAL_PORT_NAME = "/dev/ttyUSB0"
SERIAL_BAUD_RATE = 115200
MODBUS_ADDRESS = 1


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

    def __init__(self, portname=SERIAL_PORT_NAME, slaveaddress=MODBUS_ADDRESS):
        minimalmodbus.Instrument.__init__(self, portname, slaveaddress)
        self.debug = False
        self.serial.baudrate = SERIAL_BAUD_RATE

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

    # Controller related
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

    def set_ctl_rtc_clock(self, year, mon, mday, hrs, mins, secs):
        word0 = ((mins << 8) & 0xFF00) | secs  # mins : secs
        word1 = ((mday << 8) & 0xFF00) | hrs   # mday : hours
        word2 = ((year << 8) & 0xFF00) | mon   # year : mon
        return self.write_registers(int(0x9013), [word0, word1, word2])
