#!/usr/bin/python

__author__ = "James Park"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"

import os
import sys
import unittest
import subprocess
import string
import random
import logging
from time import struct_time

# Import mocked device to test against.
from mock_tracerbn2 import MockTracerBN2

# Import items under test.
sys.path.append('../')
from mhtracerbn import find_serial_port
from mhtracerbn import TracerBN

# Setup logging
FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)


class TestTracerBN(unittest.TestCase):
    """ This is a test case to provide unit tests for the tracerbn driver.

        This test case relies on the MockTracerBN class which
        needs to imported from mock_tracer for it to function.

    """

    def setUp(self):
        """ Setup mock device, fds, and tranerbn driver. """

        rand_str = ''.join(random.choice(string.ascii_lowercase) for i in range(7))

        # Device and driver ends of virtual serial port.
        self.fd_s_path = '/tmp/ttymocktracerbn_%s' % rand_str
        self.fd_m_path = '/tmp/ttyUSB0_%s' % rand_str

        # Run socat in a seperate thread.
        cmd=['/usr/bin/socat','-d','-d','-d','PTY,link=%s,raw,echo=0,ispeed=115200' % self.fd_s_path,
                                             'PTY,link=%s' % self.fd_m_path]
        self.socat_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            # Create a new mock tracer.
            self.mock_tracer = MockTracerBN2(self.fd_m_path)

            # Get the tracerbn driver under test.
            self.driver = TracerBN(portname=self.fd_s_path)

        except Exception as e:
            log.error("ERROR: %s" % e)
            self.socat_proc.terminate()
            self.socat_proc.wait()
            raise(e)

    def tearDown(self):
        """ Stop and delete mock device, close file descriptors. """
        # Join the thread if required.
        if self.mock_tracer.isAlive():
            self.mock_tracer.stop()
            self.mock_tracer.join(1.0)

        self.socat_proc.terminate()
        self.socat_proc.wait()
        self.out, self.err = self.socat_proc.communicate()

        # Delete our MockTracerBN instance.
        del self.mock_tracer

    #
    # Test driver utility functions.
    #
    def test_find_serial_port_exception(self):
        """ Test find_serial_port() raises an exception if it can't find a device (device present, but no response). """
        self.assertRaises(Exception, find_serial_port, ports_list=[self.fd_s_path])

    def test_find_serial_port_success(self):
        """ Test find_serial_port() returns the device path if it successfully finds a device. """
        self.mock_tracer.start()

        returned_path = find_serial_port(ports_list=[self.fd_s_path])
        self.assertEqual(returned_path, self.fd_s_path)

    def test_read_long_tracer_signed(self):
        """ Test read_long_tracer() deals with a 4 byte signed value. """
        self.mock_tracer.start()

        value = self.driver.read_long_tracer(int(0x9990), signed=True)
        self.assertIsWithinRange(value, -2147483648, 2147483647)

    def test_read_long_tracer_unsigned(self):
        """ Test read_long_tracer() deals with a 4 byte un-signed value. """
        self.mock_tracer.start()

        value = self.driver.read_long_tracer(int(0x9991))
        self.assertIsWithinRange(value, 0, 4294967295)

    def test_read_long_tracer_signed_4dp(self):
        """ Test read_long_tracer() deals with a 4 byte signed value and 4 decimal places. """
        self.mock_tracer.start()

        value = self.driver.read_long_tracer(int(0x9992), numberOfDecimals=4, signed=True)
        self.assertIsWithinRange(value, -214748.3648, 214748.3647)


    #
    # Test battery related methods.
    #
    def test_get_batt_voltage_success(self):
        """ Test get_batt_voltage() method returns a value between 0.0 and 655.35. """
        self.assertFuncIsWithinRange(self.driver.get_batt_voltage, 0.0, 655.35)

    def test_get_batt_current_success(self):
        """ Test get_batt_current() method returns a value between -21474836.48 and 21474836.47"""
        self.assertFuncIsWithinRange(self.driver.get_batt_current, -21474836.48, 21474836.47)

    def test_get_batt_power_success(self):
        """ Test get_batt_power() method returns a value between 0.0 and 655.35. """
        self.assertFuncIsWithinRange(self.driver.get_batt_power, -327.68, 327.67)

    def test_get_batt_temp_success(self):
        """ Test get_batt_temp() method returns a value between -327.68 and 327.67. """
        self.assertFuncIsWithinRange(self.driver.get_batt_temp, -327.68, 327.67)

    def test_get_batt_soc_success(self):
        """ Test get_batt_soc() method returns a value between 0 and 65535. """
        self.assertFuncIsWithinRange(self.driver.get_batt_soc, 0, 65535)

    def test_get_batt_voltage_max_today_success(self):
        """ Test get_batt_voltage_max_today() method returns a value between 0.0 and 655.35. """
        self.assertFuncIsWithinRange(self.driver.get_batt_voltage_max_today, 0.0, 655.35)

    def test_get_batt_voltage_min_today_success(self):
        """ Test get_batt_voltage_min_today() method returns a value between 0.0 and 655.35. """
        self.assertFuncIsWithinRange(self.driver.get_batt_voltage_min_today, 0.0, 655.35)

    def test_get_batt_rated_voltage(self):
        """ Test get_batt_rated_voltage() method returns a value between 12 and 240. """
        self.assertFuncIsWithinRange(self.driver.get_batt_rated_voltage, 0, 240)

    def test_get_batt_status_success(self):
        """ Test get_batt_status() method returns an array with the expected results. """
        self.mock_tracer.start()

        returned_array = self.driver.get_batt_status()

        # Test element0 - batt status - is within range 0 to 4.
        self.assertIsWithinRange(returned_array[0], 0, 4)

        # Test element1 - batt temp status - is within range 0 to 2.
        self.assertIsWithinRange(returned_array[1], 0, 2)

        # Test element2 - BIR fault flag - is a boolean.
        self.assertIsWithinRange(returned_array[2], 0, 1)

        # Test element3 - wrong id for rated voltage flag - is a boolean.
        self.assertIsWithinRange(returned_array[3], 0, 1)

    def test_get_charging_equip_status_success(self):
        """ Test get_charging_equip_status() method returns an array with the expected results. """
        self.mock_tracer.start()

        returned_array = self.driver.get_charging_equip_status()

        # Test element 0 - Charging Equipment Running - is a boolean.
        self.assertIsWithinRange(returned_array[0], 0, 1)

        # Test element 1 - Charging Equipment Status - is a boolean.
        self.assertIsWithinRange(returned_array[1], 0, 1)

        # Test element 2 - Charging Status - is within range 0-3.
        self.assertIsWithinRange(returned_array[2], 0, 3)

        # Test element 3 - PV Input is Short - is a boolean.
        self.assertIsWithinRange(returned_array[3], 0, 1)

        # Test element 4 - Load MOSFET is Short - is a boolean.
        self.assertIsWithinRange(returned_array[4], 0, 1)

        # Test element 5 - Load is Short - is a boolean.
        self.assertIsWithinRange(returned_array[5], 0, 1)

        # Test element 6 - Load is Over-Current - is a boolean.
        self.assertIsWithinRange(returned_array[6], 0, 1)

        # Test element 7 - Input is Over-Current - is a boolean.
        self.assertIsWithinRange(returned_array[7], 0, 1)

        # Test element 8 - Anti-Reverse MOSFET is short - is a boolean.
        self.assertIsWithinRange(returned_array[8], 0, 1)

        # Test element 9 - Charging, or Anti-Reverse MOSFET is short - is a boolean.
        self.assertIsWithinRange(returned_array[9], 0, 1)

        # Test element 10 - Charging MOSFET is short - is a boolean.
        self.assertIsWithinRange(returned_array[10], 0, 1)

        # Test element 11 - Input Voltage Status - is within range 0-3.
        self.assertIsWithinRange(returned_array[11], 0, 3)

    #
    # Test Load related methods.
    #
    def test_get_load_current_success(self):
        """ Test get_load_current() method returns a value between 0.0 and 655.35. """
        self.assertFuncIsWithinRange(self.driver.get_load_current, 0.0, 655.35)

    def test_get_load_voltage_success(self):
        """ Test get_load_voltage() method returns a value between 10.0 and 655.35. """
        self.assertFuncIsWithinRange(self.driver.get_load_voltage, 0.0, 655.35)

    def test_get_load_power_success(self):
        """ Test get_load_power() method returns a value between 0.0 and 42949672.95. """
        self.assertFuncIsWithinRange(self.driver.get_load_power, 0.0, 42949672.95)

    #
    # Test PV related methods.
    #
    def test_get_pv_power(self):
        """ Test get_pv_power() method returns a value between 0.0 and 42949672.95. """
        self.assertFuncIsWithinRange(self.driver.get_pv_power, 0.0, 42949672.95)

    def test_get_pv_current(self):
        """ Test get_pv_current() method returns a value between 0.0 and 655.35. """
        self.assertFuncIsWithinRange(self.driver.get_pv_current, 0.0, 655.35)

    def test_get_pv_voltage(self):
        """ Test get_pv_voltage() method returns a value between 0.0 and 655.35. """
        self.assertFuncIsWithinRange(self.driver.get_pv_voltage, 0.0, 655.35)

    def test_get_pv_voltage_max_today(self):
        """ Test get_pv_voltage_max_today() method returns a value between 0.0 and 655.35. """
        self.assertFuncIsWithinRange(self.driver.get_pv_voltage_max_today, 0.0, 655.35)

    def test_get_pv_voltage_min_today(self):
        """ Test get_pv_voltage_min_today() method returns a value between 0.0 and 655.35. """
        self.assertFuncIsWithinRange(self.driver.get_pv_voltage_min_today, 0.0, 655.35)


    #
    # Test controller general parameters related methods.
    #
    def test_get_night_or_day(self):
        """ Test get_night_or_day() returns a boolean value. """
        self.assertFuncIsWithinRange(self.driver.get_night_or_day, 0, 1)

    def test_get_energy_today(self):
        """ Test get_energy_today() returns a value between 0.0 and 42949672.95. """
        self.assertFuncIsWithinRange(self.driver.get_energy_today, 0.0, 42949672.95)

    def test_get_energy_month(self):
        """ Test get_energy_month() returns a value between 0.0 and 42949672.95. """
        self.assertFuncIsWithinRange(self.driver.get_energy_month, 0.0, 42949672.95)

    def test_get_energy_year(self):
        """ Test get_energy_year() returns a value between 0.0 and 42949672.95. """
        self.assertFuncIsWithinRange(self.driver.get_energy_year, 0.0, 42949672.95)

    def test_get_energy_total(self):
        """ Test get_energy_total() returns a value between 0.0 and 42949672.95. """
        self.assertFuncIsWithinRange(self.driver.get_energy_total, 0.0, 42949672.95)

    def test_get_co2_saved(self):
        """ Test get_co2_saved() returns a value between 0.0 and 42949672.95. """
        self.assertFuncIsWithinRange(self.driver.get_co2_saved, 0.0, 42949672.95)


    #
    # Controller Clock related.
    #
    def test_get_ctl_rtclock_sec(self):
        """ Test get_ctl_rtclock_sec() returns a value between 0 and 59. """
        self.assertFuncIsWithinRange(self.driver.get_ctl_rtclock_sec, 0, 59)

    def test_get_ctl_rtclock_min(self):
        """ Test get_ctl_rtclock_min() returns a value between 0 and 59. """
        self.assertFuncIsWithinRange(self.driver.get_ctl_rtclock_min, 0, 59)

    def test_get_ctl_rtclock_hour(self):
        """ Test get_ctl_rtclock_hour() returns a value between 0 and 23. """
        self.assertFuncIsWithinRange(self.driver.get_ctl_rtclock_hour, 0, 23)

    def test_get_ctl_rtclock_day(self):
        """ Test get_ctl_rtclock_day() returns a value between 1 and 31. """
        self.assertFuncIsWithinRange(self.driver.get_ctl_rtclock_day, 1, 31)

    def test_get_ctl_rtclock_month(self):
        """ Test get_ctl_rtclock_month() returns a value between 1 and 12. """
        self.assertFuncIsWithinRange(self.driver.get_ctl_rtclock_month, 1, 12)

    def test_get_ctl_rtclock_year(self):
        """ Test get_ctl_rtclock_year() returns a value between 0 and 99. """
        self.assertFuncIsWithinRange(self.driver.get_ctl_rtclock_year, 0, 99)

    def test_get_ctl_rtclock_time(self):
        """ Test get_ctl_rtclock_time() returns an instance of a time.struct_time. """
        # This functon will make 6 modbus requests; Y, M, D, h, m and seconds.
        self.mock_tracer._num_of_requests = 6

        self.mock_tracer.start()

        t = self.driver.get_ctl_rtclock_time()
        self.assertEqual(struct_time, type(t))

    #
    # Custom assert functions for similar tests.
    #
    def assertFuncIsWithinRange(self, funct, min_value, max_value):
        """ Test a driver method returns a value between a given range. """
        self.mock_tracer.start()

        # Execute the driver method to fetch the result.
        x = funct()

        self.assertIsWithinRange(x, min_value, max_value)

    def assertIsWithinRange(self, x, min_value, max_value):
        """ Test x is between, or equal to the given range. """

        if min_value <= max_value:
            # Test the result is within the given range.
            self.assertGreaterEqual(x, min_value)
            self.assertLessEqual(x, max_value)
        else:
            raise("max and min value must be just that, not min=%s, max=%s." % (min_value, max_value))


if __name__ == "__main__":
    unittest.run()
