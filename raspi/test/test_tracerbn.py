#!/usr/bin/python

__author__ = "James Park"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"

import os
import pty
import unittest

# Import items under test.
from tracerbn import switch_4_bytes
from tracerbn import find_serial_port
from tracerbn import TracerBN

# Import item to test against.
from mock_tracerbn import MockTracerBN


class TestTracerBN(unittest.TestCase):
    """ This is a test case to provide unit tests for the tracerbn driver.

        This test case relies on the MockTracerBN class which
        needs to imported from mock_tracer for it to function.

    """

    def setUp(self):
        """ Setup mock device, fds, and tranerbn driver. """
        # Get new pty master slave ends
        self.fd_m, self.fd_s = pty.openpty()

        # Set slave device path
        self.fd_s_path = os.ttyname(self.fd_s)

        # Create a new mock tracer
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

    def test_switch_4_bytes(self):
        """ Test switch_4_bytes() function. """
        a = 0x89AB0000
        b = 0x0000CDEF
        correct_result = (a >> 16) | (b << 16)
        self.assertEquals(switch_4_bytes(a | b), correct_result)

    def test_find_serial_port_exception(self):
        """ Test find_serial_port() raises an exception if it can't find a device (present but no response). """
        self.assertRaises(Exception, find_serial_port, ports_list=[self.fd_s_path])

    def test_find_serial_port_success(self):
        """ Test find_serial_port() returns the device path if it successfully finds a device. """
        self.mock_tracer.start()

        returned_path = find_serial_port(ports_list=[self.fd_s_path])
        self.assertEqual(returned_path, self.fd_s_path)

    #
    # Test battery related methods
    #
    def test_get_batt_voltage_success(self):
        """ Test get_batt_voltage() method returns a value between 10.0 and 15.0. """
        self.assertFuncIsWithinRange(self.driver.get_batt_voltage, 10.0, 15.0)

    def test_get_batt_current_success(self):
        """ Test get_batt_current() method returns a value between -30.0 and 30.0. """
        self.assertFuncIsWithinRange(self.driver.get_batt_current, -30.0, 30.0)

    def test_get_batt_power_success(self):
        """ Test get_batt_power() method returns a value between 0.0 and 150.0. """
        self.assertFuncIsWithinRange(self.driver.get_batt_power, 0.0, 150.0)

    def test_get_batt_temp_success(self):
        """ Test get_batt_temp() method returns a value between -50.0 and 150.0. """
        self.assertFuncIsWithinRange(self.driver.get_batt_temp, -50.0, 150.0)

    def test_get_batt_soc_success(self):
        """ Test get_batt_soc() method returns a value between 0.0 and 100.0. """
        self.assertFuncIsWithinRange(self.driver.get_batt_soc, 0, 100)

    def test_get_batt_voltage_max_today_success(self):
        """ Test get_batt_voltage_max_today() method returns a value between 10.0 and 20.0. """
        self.assertFuncIsWithinRange(self.driver.get_batt_voltage_max_today, 10.0, 20.0)

    def test_get_batt_voltage_min_today_success(self):
        """ Test get_batt_voltage_min_today() method returns a value between 10.0 and 20.0. """
        self.assertFuncIsWithinRange(self.driver.get_batt_voltage_min_today, 10.0, 20.0)

    def test_get_batt_rated_voltage(self):
        """ Test get_batt_rated_voltage() method returns a value between 12 and 240. """
        self.assertFuncIsWithinRange(self.driver.get_batt_rated_voltage, 12, 240)

    def test_get_batt_status_success(self):
        """ Test get_batt_status() method returns an array with the expected results. """

        # Start the tracer.
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

        # Start the tracer.
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

    def test_get_load_current_success(self):
        """ Test get_load_current() method returns a value between 0.0 and 30.0. """
        self.assertFuncIsWithinRange(self.driver.get_load_current, 0.0, 30.0)

    def test_get_load_voltage_success(self):
        """ Test get_load_voltage() method returns a value between 10.0 and 20.0. """
        self.assertFuncIsWithinRange(self.driver.get_load_voltage, 0.0, 20.0)

    def test_get_load_power_success(self):
        """ Test get_load_power() method returns a value between 0.0 and 360.0. """
        self.assertFuncIsWithinRange(self.driver.get_load_power, 0.0, 360.0)

    def assertFuncIsWithinRange(self, funct, min_value, max_value):
        """ Assert method to test a driver method returns values within a given range. """

        # Start the tracer.
        self.mock_tracer.start()

        # Execute the driver method to fetch the result.
        x = funct()

        self.assertIsWithinRange(x, min_value, max_value)

    def assertIsWithinRange(self, x, min_value, max_value):
        """ Assert method to test x is within, or equal to the given values. """

        if min_value <= max_value:
            # Test the result is within the given range.
            self.assertGreaterEqual(x, min_value)
            self.assertLessEqual(x, max_value)
        else:
            raise("max and min value must be just that, not min=%s, max=%s." % (min_value, max_value))


if __name__ == "__main__":
    unittest.run()
