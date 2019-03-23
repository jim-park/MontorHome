#!/usr/bin/python

__author__ = "James Park"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"

import os
import pty
import unittest
from time import struct_time

# Import items under test.
from tracerbn import find_serial_port
from tracerbn import TracerBN

# Import mocked device to test against.
from mock_tracerbn import MockTracerBN


class TestTracerBN(unittest.TestCase):
    """ This is a test case to provide unit tests for the tracerbn driver.

        This test case relies on the MockTracerBN class which
        needs to imported from mock_tracer for it to function.

    """

    def setUp(self):
        """ Setup mock device, fds, and tranerbn driver. """
        # Get new pty master slave ends.
        self.fd_m, self.fd_s = pty.openpty()

        # Set slave device path.
        self.fd_s_path = os.ttyname(self.fd_s)

        # Create a new mock tracer.
        self.mock_tracer = MockTracerBN(self.fd_m)

        # Get the tracerbn driver under test.
        self.driver = TracerBN(portname=self.fd_s_path)

    def tearDown(self):
        """ Stop and delete mock device, close file descriptors. """
        # Join the thread if required.
        if self.mock_tracer.isAlive():
            self.mock_tracer.join(1.0)

        # Close our pty master and slave ends.
        os.close(self.fd_m)
        os.close(self.fd_s)

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
        self.assertFuncIsWithinRange(self.driver.get_batt_power, 0.0, 655.35)

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
        print returned_array

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
        self.mock_tracer.num_of_requests = 6

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
