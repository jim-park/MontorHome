#!/usr/bin/python

__author__ = "James Park"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"

import os
import threading
import minimalmodbus
from minimalmodbus import MODE_RTU
from random import randrange


def get_two_bytes(data):
    """Return a list of the two lsbytes from an int."""
    return (data & 0xFF), (data >> 8) & 0xFF


def get_four_bytes(data):
    """Return a list of the four lsbytes from an int."""
    return (data & 0xFF), (data >> 8) & 0xFF, (data >> 16) & 0xFF, (data >> 24) & 0xFF


def get_two_byte_bytearray(data):
    """Return a list of the two lsbytes from an int, plus their count at element 0."""
    byte0, byte1 = get_two_bytes(data)
    return bytearray([2, byte1, byte0])


def get_four_byte_bytearray(data):
    """Return a list of the four lsbytes from an int (reversed), plus their count at element 0."""
    byte0, byte1, byte2, byte3 = get_four_bytes(data)
    # Note the byte order.
    return bytearray([4, byte1, byte0, byte3, byte2])


class RequestCodes:
    """Raw modbus request codes."""
    device_info = bytearray([0x01, 0x2b, 0x0e, 0x01, 0x00, 0x70, 0x77])
    batt_voltage = bytearray([0x01, 0x04, 0x33, 0x1A, 0x00, 0x01, 0x1F, 0x49])
    batt_current = bytearray([0x01, 0x04, 0x33, 0x1B, 0x00, 0x02, 0x0E, 0x88])
    batt_power = bytearray([0x01, 0x04, 0x31, 0x06, 0x00, 0x02, 0x9F, 0x36])
    batt_temp = bytearray([0x01, 0x04, 0x31, 0x1B, 0x00, 0x01, 0x4F, 0x31])
    batt_soc = bytearray([0x01, 0x04, 0x31, 0x1A, 0x00, 0x01, 0x1E, 0xF1])
    batt_voltage_max_today = bytearray([0x01, 0x04, 0x33, 0x02, 0x00, 0x01, 0x9F, 0x4E])
    batt_voltage_min_today = bytearray([0x01, 0x04, 0x33, 0x03, 0x00, 0x01, 0xCE, 0x8E])

    def __init__(self): pass


class MockTracerBN(threading.Thread):
    """This acts as a poor mans TracerBN emulator. It runs in a separate thread,
        when it receives a modbus request, it services the request with sensible
        values, then immediately terminates."""

    def __init__(self, fd):
        threading.Thread.__init__(self)
        self.fd = fd
        print "MockTracer created"

    def run(self):
        """Service one request and exit. No loops."""

        print "MockTracer running"

        rx_request = os.read(self.fd, 1024)
        print "MockTracer rcvd: " + rx_request

        # Request for device information.
        if rx_request == RequestCodes.device_info:
            print "Request for device information"
            # Return a string containing 'Tracer'.
            tx_string = "1234xyx+_&^$#Tracer#xyx+_&^$#4321"
            # Send string.
            self.send(tx_string)

        # Request for battery voltage.
        elif rx_request == RequestCodes.batt_voltage:
            print "Request for batt voltage"
            # Voltage returned is x100. 2 bytes. 10.00V to 15.00V.
            self.send(get_two_byte_bytearray(randrange(1000, 1500)))

        # Request for battery current.
        elif rx_request == RequestCodes.batt_current:
            print "Request for batt current"
            # Current returned is x100. 4 bytes. -30.00A to 30.00A.
            self.send(get_four_byte_bytearray(randrange(-3000, 3000)))

        # Request for battery power.
        elif rx_request == RequestCodes.batt_power:
            print "Request for batt power"
            # Power returned is x100. 4 bytes. 0.00W to 150.00W.
            self.send(get_four_byte_bytearray(randrange(0, 15000)))

        # Request for battery temperature.
        elif rx_request == RequestCodes.batt_temp:
            print "Request for batt temperature"
            # Temperature returned is x100. 2 bytes -10.00 to 150.00 degC.
            self.send(get_two_byte_bytearray(randrange(-1000, 15000)))

        # Request for battery soc.
        elif rx_request == RequestCodes.batt_soc:
            print "Request for batt SOC"
            # SOC is returned as a percentage. 2 bytes.
            self.send(get_two_byte_bytearray(randrange(0, 100)))

        # Request for battery max voltage today.
        elif rx_request == RequestCodes.batt_voltage_max_today:
            print "Request for batt max voltage today"
            # Max voltage today returned is x100. 2 bytes. 10.00V to 20.00V.
            self.send(get_two_byte_bytearray(randrange(1000, 2000)))

        # Request for battery min voltage today.
        elif rx_request == RequestCodes.batt_voltage_min_today:
            print "Request for batt max voltage today"
            # Min voltage today returned is x100. 2 bytes. 10.00V to 20.00V.
            self.send(get_two_byte_bytearray(randrange(1000, 2000)))

        print "MockTracer exiting"

    def send(self, tx_data):
        """Write response data back to the driver"""
        # Allow minimalmodbus to put the final response together for us, adding the crc.
        resp = minimalmodbus._embedPayload(1, MODE_RTU, 4, '%s' % tx_data)
        # Send response.
        print "MockTracer send: %s (%d)" % (resp, os.write(self.fd, resp))
