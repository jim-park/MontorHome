#!/usr/bin/env python

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


class TracerBN(minimalmodbus.Instrument):
    """ Instrument class for Tracer BN Series MPPT solar charger controller.

    Communicates via ModBus RTU protocol (over RS232 or RS485), using the *MinimalModbus* Python module.

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
    from Jarkko Sonninens' excellent github page at https://github.com/kasbert/epsolar-tracer.

    """

    def __init__(self, portname=DEFAULT_SERIAL_PORT_NAME, slaveaddress=DEFAULT_MODBUS_ADDRESS):
        minimalmodbus.Instrument.__init__(self, portname, slaveaddress)
        self.serial.baudrate = DEFAULT_SERIAL_BAUD_RATE
        self.debug = False      # Set minimalmodbus debugging on or off
        self.serial.flush()     # Flush the serial buffer, before we begin

    #
    # Wrapper for minimalmonbus read_long() method.
    #
    def read_long_tracer(self, registeraddress, numberOfDecimals=0, functioncode=4, signed=False):
        """ Read 2 registers (32-bits) from the tracerbn. Deal with negative values and divisors. """
        # Read long data using minimalmodbus
        data = self.read_long(registeraddress=registeraddress, functioncode=functioncode, signed=signed)

        # Swap around the top and bottom pairs of bytes.
        data = ((int(data) & 0xFFFF0000) >> 16) | ((int(data) & 0x0000FFFF) << 16)

        # If we are a signed number, compute the 2's complement of data.
        if signed and (data & (1 << (32 - 1))) != 0:
            data = data - (1 << 32)         # compute negative value

        # Divide by the number of dps specified.
        if numberOfDecimals > 0:
            data = data / (10.0 ** numberOfDecimals)

        return data

    #
    # Wrappers for minimalmodbus read_register() method.
    #
    def read_register_low_byte(self, registeraddress, numberOfDecimals=0, functioncode=3, signed=False):
        """ Return the low byte of a 16-bit register. """
        return self.read_register(registeraddress, numberOfDecimals, functioncode, signed) & 0xFF

    def read_register_high_byte(self, registeraddress, numberOfDecimals=0, functioncode=3, signed=False):
        """ Return the high byte of a 16-bit register. """
        return (self.read_register(registeraddress, numberOfDecimals, functioncode, signed) >> 8) & 0xFF

    #
    # Battery related.
    #
    def get_batt_rated_voltage(self):
        """ Return a float indicating the rated battery voltage. """
        return self.read_register(int(0x3004), 2, 4)

    def get_batt_voltage(self):
        """ Return a float indicating the instantaneous battery voltage in Volts. """
        return self.read_register(int(0x331A), 2, 4)

    def get_batt_current(self):
        """ Return a signed float indicating the instantaneous battery current in Amperes. """
        return self.read_long_tracer(int(0x331B), 2, 4, signed=True)

    def get_batt_power(self):
        """ Return a float indicating the instantaneous charging power of the battery in Watts. """
        return self.read_long_tracer(int(0x3106), 2, 4, signed=True)

    def get_batt_temp(self):
        """ Return a signed float indicating the temperature from the battery temperature sensor in degC. """
        return self.read_register(int(0x311B), 2, 4, signed=True)

    def get_batt_rated_capacity(self):
        """ Return an int indicating the rated capacity of the battery in Volts. """
        return self.read_register(int(0x9001), 0, 3)

    def get_batt_soc(self):
        """ Return an int indicating the State of Charge (SOC) of the battery as a percentage. """
        return self.read_register(int(0x311A), 0, 4)

    def get_batt_voltage_max_today(self):
        """ Return a float indicating the maximum voltage the battery has reached today in Volts. """
        return self.read_register(int(0x3302), 2, 4)

    def get_batt_voltage_min_today(self):
        """ Return a float indicating the minimum voltage the battery has been at today in Volts. """
        return self.read_register(int(0x3303), 2, 4)

    def set_batt_rated_capacity(self, capacity):
        """ Set the rated capacity of the battery in Ah. """
        return self.write_register(int(0x9001), capacity, 0)

    def get_batt_status(self):
        """ Return an array containing 4 elements indicating the battery status. """
        statuses = int(self.read_register((int(0x3200)), 0, 4))
        # statuses contains four parameters to read (unpack) from various bits across the 2 bytes received.

        # Battery Status, comprises bits 0-3, they hold values 0-4 only. They indicate;
        #   (0) Normal | (1) Overvolt | (2) Undervolt | (3) Low volt disconnect | (4) Fault
        batt_status = statuses & 0x000F

        # Battery Temperature Status, comprises, bits 4-7, they hold values 0-2 only. They indicate;
        #   (0) Normal | (1) Over temperature | (2) Low temperature
        batt_temp_status = (statuses & 0x00F0) >> 4

        # Battery Internal Resistance Abnormal Flag, comprises bit 8. It's a boolean. It indicates;
        #    (0) BIR normal | (1) BIR abnormal
        bir_fault = (statuses & 0x0100) >> 8

        # Wrong Identification For Battery Rated Voltage Flag. It's a boolean. It indicates;
        #     (0) Correct id for rated voltage | (1) Wrong id for rated voltage
        batt_rated_voltage_fault = (statuses & 0x8000) >> 15

        print "drv: status: %d, temp status: %d, bir fault: %d, rated voltage fault: %d" % \
              (batt_status, batt_temp_status, bir_fault, batt_rated_voltage_fault)

        return [batt_status, batt_temp_status, bir_fault, batt_rated_voltage_fault]

    def get_charging_equip_status(self):
        """ Return an array containing 12 elements indicating various charging status details. """
        statuses = int(self.read_register((int(0x3201)), 0, 4))
        # statuses contains 12 parameters to read (unpack) from various bits across the 2 bytes received.

        # Charging Equipment Running, comprises bit 0, it's a boolean. It indicates;
        #   (0) Standby | (1) Running
        charging_equip_running = statuses & 0x0001

        # Charging Equipment Status, comprises bit 1, it's a boolean. It indicates;
        #   (0) Normal | (1) Fault
        charging_equip_status = (statuses & 0x0002) >> 1

        # Charging Status, comprises bits 2-3, holds the values 0-3. It indicates;
        #   (0) No Charging | (1) Float | (2) Boost | (3) Equalisation
        charging_status = (statuses & 0x000C) >> 2

        # PV Input is Short, comprises bit 4. It's a boolean. It indicates;
        #   (0) Normal | (1) Short
        pv_input_short = (statuses & 0x0010) >> 4

        # Load MOSFET is Short, comprises bit 7. It's a boolean. It indicates;
        #   (0) Normal | (1) Short
        load_mosfet_short = (statuses & 0x0080) >> 7

        # Load is Short, comprises bit 8. It's a boolean. It indicates;
        #   (0) Normal | (1) Short
        load_short = (statuses & 0x0100) >> 8

        # Load is Over-Current, comprises bit 9. It's a boolean. It indicates;
        #   (0) Normal | (1) Short
        load_over_current = (statuses & 0x0200) >> 9

        # Input is Over-Current, comprises bit 10. It's a boolean. It indicates;
        #   (0) Normal | (1) Short
        input_over_current = (statuses & 0x0400) >> 10

        # Anti-Reverse MOSFET is short, comprises bit 11. It's a boolean. It indicates;
        #   (0) Normal | (1) Short
        anti_rev_mosfet_short = (statuses & 0x0800) >> 11

        # Charging, or Anti-Reverse MOSFET is short, comprises bit 12. It's a boolean. It indicates;
        #   (0) Normal | (1) Short
        anti_rev_or_charging_mosfet_short = (statuses & 0x1000) >> 12

        # Charging MOSFET is short, comprises bit 13. It's a boolean. It indicates;
        #   (0) Normal | (1) Short
        charging_mosfet_short = (statuses & 0x2000) >> 13

        # Input Voltage Status, comprises bits 14-15, they hold values 0-3 only. They indicate;
        #   (0) Normal | (1) No power connected | (2) High voltage input | (3) Input voltage error
        input_voltage_status = (statuses & 0xC000) >> 14

        # Put it all into an array.
        rtn_array = [charging_equip_running,
                     charging_equip_status,
                     charging_status,
                     pv_input_short,
                     load_mosfet_short,
                     load_short,
                     load_over_current,
                     input_over_current,
                     anti_rev_mosfet_short,
                     anti_rev_or_charging_mosfet_short,
                     charging_mosfet_short,
                     input_voltage_status]

        return rtn_array

    #
    # Load related.
    #
    def get_load_current(self):
        """ Return the instantaneous load current in Amperes. """
        return self.read_register(int(0x310D), 2, 4)

    def get_load_power(self):
        """ Return the instantaneous load power in Watts. """
        return self.read_long_tracer(int(0x310E), numberOfDecimals=2)

    def get_load_voltage(self):
        """ Return the instantaneous load voltage in Volts. """
        return self.read_register(int(0x310C), 2, 4)

    #
    # PV related.
    #
    def get_pv_power(self):
        """ Return the instantaneous PV power in Volts. """
        return self.read_long_tracer(int(0x3102), numberOfDecimals=2)

    def get_pv_current(self):
        """ Return the instantaneous PV input current in Amperes. """
        return self.read_register(int(0x3101), 2, 4)

    def get_pv_voltage(self):
        """ Return the instantaneous PV voltage in Volts. """
        return self.read_register(int(0x3100), 2, 4)

    def get_pv_voltage_max_today(self):
        """ Return the maximum voltage the PV has reached today in Volts. """
        return self.read_register(int(0x3300), 2, 4)

    def get_pv_voltage_min_today(self):
        """ Return the minimum voltage the PV has been at today in Volts. """
        return self.read_register(int(0x3301), 2, 4)

    #
    # Controller general parameters.
    #
    def get_night_or_day(self):
        """ Return night or day (1 or 0 respectively) from the controller. """
        return self.read_bit(int(0x200C))

    def get_energy_today(self):
        """ Return the energy generated today in kWHrs. """
        return self.read_long_tracer(int(0x330C), numberOfDecimals=2)

    def get_energy_month(self):
        """ Return the energy generated this month in kWHrs. """
        return self.read_long_tracer(int(0x330E), numberOfDecimals=2)

    def get_energy_year(self):
        """ Return the energy generated this year in kWHrs. """
        return self.read_long_tracer(int(0x3310), numberOfDecimals=2)

    def get_energy_total(self):
        """ Return the total energy generated in kWHrs. """
        return self.read_long_tracer(int(0x3312), numberOfDecimals=2)

    def get_co2_saved(self):
        """ Return the total co2 saved in Tonnes. """
        return self.read_long_tracer(int(0x3314), numberOfDecimals=2)

    #
    # Controller Clock related.
    #
    def get_ctl_rtclock_sec(self):
        """ Return the controller rtc seconds. """
        return self.read_register_low_byte(int(0x9013), 0, 3)

    def get_ctl_rtclock_min(self):
        """ Return the controller rtc minutes. """
        return self.read_register_high_byte(int(0x9013), 0, 3)

    def get_ctl_rtclock_hour(self):
        """ Return the controller rtc hours. """
        return self.read_register_low_byte(int(0x9014), 0, 3)

    def get_ctl_rtclock_day(self):
        """ Return the controller rtc day of month. """
        return self.read_register_high_byte(int(0x9014), 0, 3)

    def get_ctl_rtclock_month(self):
        """ Return the controller rtc month. """
        return self.read_register_low_byte(int(0x9015), 0, 3)

    def get_ctl_rtclock_year(self):
        """ Return the controller rtc year. """
        return self.read_register_high_byte(int(0x9015), 0, 3)

    def get_ctl_rtclock_time(self):
        """ Return the controller time as a time object. """
        t_str = "%s %s %s %s %s %s" % (self.get_ctl_rtclock_year(),
                                        self.get_ctl_rtclock_month(),
                                        self.get_ctl_rtclock_day(),
                                        self.get_ctl_rtclock_hour(),
                                        self.get_ctl_rtclock_min(),
                                        self.get_ctl_rtclock_sec())

        return time.strptime(t_str, "%y %m %d %H %M %S")

    def set_ctl_rtclock(self, year, mon, mday, hrs, mins, secs):
        """ All time registers must be written at once
            year must be a 2 digit number, not 4. """
        word0 = ((mins << 8) & 0xFF00) | secs  # mins : secs
        word1 = ((mday << 8) & 0xFF00) | hrs   # mday : hours
        word2 = ((year << 8) & 0xFF00) | mon   # year : mon
        return self.write_registers(int(0x9013), [word0, word1, word2])

    def set_ctl_rtclock_localtime(self):
        """ Set the time on the tracer to localtime. """
        t = time.localtime()
        year = int(time.strftime("%y", t))      # Tracer expects a 2 digit year.
        return self.set_ctl_rtclock(year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)


#
# Interrogate serial ports for a TracerBN device.
#
def find_serial_port(ports_list=None):
    """ Return the port path once the device is identified, otherwise raise an exception. """

    device_info_request = bytearray([0x01, 0x2b, 0x0e, 0x01, 0x00, 0x70, 0x77])  # Raw device information request

    if not ports_list:
        # This pythonic line of code creates a list of device paths (containing the
        # string "ttyUSB") from the /dev directory.  e.g ["/dev/ttyUSB0", "/dev/ttyUSB2"].
        ports_list = ["/dev/%s" % s for s in os.listdir('/dev') if "ttyUSB" in s]

    for port in ports_list:

        try:
            with serial.Serial(port=port, baudrate=DEFAULT_SERIAL_BAUD_RATE, timeout=1.0) as s:
                s.write(device_info_request)
                dev_info = s.read(int(62))  # read 62 bytes of device information returned

                if dev_info.find("Tracer") is not -1:
                    print "Found TracerBN on %s" % port
                    return port
                else:
                    print "A device is present at %s, but is not a TracerBN" % port

        except (serial.SerialException, serial.SerialTimeoutException):
            print "Failed to find device on port %s" % port

    # If we haven't found a device on a port by this point,
    # raise an exception. The device cannot be found.
    raise Exception('Failed to find TracerBN on any port')
