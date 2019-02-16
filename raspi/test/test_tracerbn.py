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

    def setUp(self):
        # Get new pty master slave ends
        self.fd_m, self.fd_s = pty.openpty()

        # Set slave device path
        self.fd_s_path = os.ttyname(self.fd_s)

        # Create a new mock tracer
        self.mock_tracer = MockTracerBN(self.fd_m)

        # Get the tracer driver under test
        self.driver = TracerBN(portname=self.fd_s_path)

    def tearDown(self):
        # Join the thread if required.
        if self.mock_tracer.isAlive():
            self.mock_tracer.join(1.0)

        # Close our pty master and slave ends.
        os.close(self.fd_m)
        os.close(self.fd_s)

        # Delete our MockTracerBN instance.
        del self.mock_tracer

    def test_switch_4_bytes(self):
        a = 0x89AB0000
        b = 0x0000CDEF
        correct_result = (a >> 16) | (b << 16)
        self.assertEquals(switch_4_bytes(a | b), correct_result)

    def test_find_serial_port_exception(self):
        # Call find_serial_port function without the mock Tracer running (present but no response).
        self.assertRaises(Exception, find_serial_port, ports_list=[self.fd_s_path])

    def test_find_serial_port_success(self):
        # Start the tracer
        self.mock_tracer.start()
        # Call find_serial_port function with the mock Tracer running (we expect the correct response).
        returned_path = find_serial_port(ports_list=[self.fd_s_path])
        self.assertEqual(returned_path, self.fd_s_path)

    #
    # Test battery related methods
    #
    def test_get_batt_voltage_success(self):
        # We expect a random voltage value in the range 10.00 < v < 15.00.
        self.within_range(self.driver.get_batt_voltage, 10.0, 15.0)

    def test_get_batt_current_success(self):
        # We expect a random current value in the range 30.00 < A < 30.00.
        self.within_range(self.driver.get_batt_current, -30.0, 30.0)

    def test_get_batt_power_success(self):
        # We expect a random power value in the range 0.00 < W < 150.00.
        self.within_range(self.driver.get_batt_power, 0.0, 150.0)

    def test_get_batt_temp_success(self):
        """TracerBN.get_batt_temp"""
        # We expect a random temperature value in the range -50 < degC < 150.00.
        self.within_range(self.driver.get_batt_temp, -50.0, 150)

    def test_get_batt_soc_success(self):
        """TracerBN.get_batt_soc"""
        # We expect a random percentage in the range 0 < % < 100.
        self.within_range(self.driver.get_batt_soc, 0, 100)

    def test_get_batt_voltage_max_today_success(self):
        # We expect a random voltage in the range 10 < V < 20.
        self.within_range(self.driver.get_batt_voltage_max_today, 10, 20)

    def test_get_batt_voltage_min_today_success(self):
        # We expect a random voltage in the range 10 < V < 20.
        self.within_range(self.driver.get_batt_voltage_min_today, 10, 20)

    def within_range(self, funct, min_value, max_value):
        """Generic function to test driver returns values within a given range"""

        # Start the tracer.
        self.mock_tracer.start()

        # Execute the function to fetch the result.
        x = funct()

        # Test the result is within the given range.
        self.assertGreaterEqual(x, min_value)
        self.assertLessEqual(x, max_value)


if __name__ == "__main__":
    unittest.run()
