#!/usr/bin/python

__author__ = "James Park"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"

import os
import threading
import minimalmodbus
from minimalmodbus import MODE_RTU
from random import randrange, randint


def get_two_bytes(data):
    """ Return a list of the two lsbytes from an int. """
    return (data & 0xFF), (data >> 8) & 0xFF


def get_four_bytes(data):
    """ Return a list of the four lsbytes from an int. """
    return (data & 0xFF), (data >> 8) & 0xFF, (data >> 16) & 0xFF, (data >> 24) & 0xFF


def get_two_byte_bytearray(data):
    """ Return a list of the two lsbytes from an int, plus their count at element 0. """
    byte0, byte1 = get_two_bytes(data)
    return bytearray([2, byte1, byte0])


def get_four_byte_bytearray(data):
    """ Return a list of the four lsbytes from an int (reversed), plus their count at element 0. """
    byte0, byte1, byte2, byte3 = get_four_bytes(data)
    # Note the byte order.
    return bytearray([4, byte1, byte0, byte3, byte2])


class RequestCodes:
    """ Raw modbus request codes. """
    device_info = bytearray([0x01, 0x2b, 0x0e, 0x01, 0x00, 0x70, 0x77])
    batt_voltage = bytearray([0x01, 0x04, 0x33, 0x1A, 0x00, 0x01, 0x1F, 0x49])
    batt_current = bytearray([0x01, 0x04, 0x33, 0x1B, 0x00, 0x02, 0x0E, 0x88])
    batt_power = bytearray([0x01, 0x04, 0x31, 0x06, 0x00, 0x02, 0x9F, 0x36])
    batt_temp = bytearray([0x01, 0x04, 0x31, 0x1B, 0x00, 0x01, 0x4F, 0x31])
    batt_soc = bytearray([0x01, 0x04, 0x31, 0x1A, 0x00, 0x01, 0x1E, 0xF1])
    batt_voltage_max_today = bytearray([0x01, 0x04, 0x33, 0x02, 0x00, 0x01, 0x9F, 0x4E])
    batt_voltage_min_today = bytearray([0x01, 0x04, 0x33, 0x03, 0x00, 0x01, 0xCE, 0x8E])
    batt_status = bytearray([0x01, 0x04, 0x32, 0x00, 0x00, 0x01, 0x3F, 0x72])
    batt_rated_voltage = bytearray([0x01, 0x04, 0x30, 0x04, 0x00, 0x01, 0x7F, 0x0B])
    charging_equip_status = bytearray([0x01, 0x04, 0x32, 0x01, 0x00, 0x01, 0x6E, 0xB2])
    load_current = bytearray([0x01, 0x04, 0x31, 0x0D, 0x00, 0x01, 0xAE, 0xF5])
    load_voltage = bytearray([0x01, 0x04, 0x31, 0x0C, 0x00, 0x01, 0xFF, 0x35])
    load_power = bytearray([0x01, 0x04, 0x31, 0x0E, 0x00, 0x02, 0x1E, 0xF4])

    def __init__(self): pass


class MockTracerBN(threading.Thread):
    """ This acts as a poor mans TracerBN emulator. It runs in a seperate thread.
        When it receives a modbus request, it services the request with a sensible
        response, then immediately terminates.
    """

    def __init__(self, fd):
        threading.Thread.__init__(self)
        self.fd = fd
        print "MockTracer created"

    def run(self):
        """ Service one request and exit. No loops. """

        print "MockTracer running"

        rx_request = os.read(self.fd, 1024)
        print "MockTracer rcvd: " + rx_request

        # Request for device information.
        if rx_request == RequestCodes.device_info:
            # Return a string containing 'Tracer'.
            tx_string = "1234xyx+_&^$#Tracer#xyx+_&^$#4321"
            # Send string.
            self.send(tx_string)

        # Request for battery voltage.
        elif rx_request == RequestCodes.batt_voltage:
            # Voltage returned is x100. 2 bytes. 10.00V to 15.00V.
            self.send(get_two_byte_bytearray(randrange(1000, 1500)))

        # Request for battery current.
        elif rx_request == RequestCodes.batt_current:
            # Current returned is x100. 4 bytes. -30.00A to 30.00A.
            self.send(get_four_byte_bytearray(randrange(-3000, 3000)))

        # Request for battery power.
        elif rx_request == RequestCodes.batt_power:
            # Power returned is x100. 4 bytes. 0.00W to 150.00W.
            self.send(get_four_byte_bytearray(randrange(0, 15000)))

        # Request for battery temperature.
        elif rx_request == RequestCodes.batt_temp:
            # Temperature returned is x100. 2 bytes -10.00 to 150.00 degC.
            self.send(get_two_byte_bytearray(randrange(-1000, 15000)))

        # Request for battery soc.
        elif rx_request == RequestCodes.batt_soc:
            # SOC is returned as a percentage. 2 bytes.
            self.send(get_two_byte_bytearray(randrange(0, 100)))

        # Request for battery max voltage today.
        elif rx_request == RequestCodes.batt_voltage_max_today:
            # Max voltage today returned is x100. 2 bytes. 10.00V to 20.00V.
            self.send(get_two_byte_bytearray(randrange(1000, 2000)))

        # Request for battery min voltage today.
        elif rx_request == RequestCodes.batt_voltage_min_today:
            # Min voltage today returned is x100. 2 bytes. 10.00V to 20.00V.
            self.send(get_two_byte_bytearray(randrange(1000, 2000)))

        # Request for rated battery voltage
        elif rx_request == RequestCodes.batt_rated_voltage:
            # Rated voltage returned 'should' be one of 9 discrete V values x100. 2 bytes. 12V to 240V.
            self.send(get_two_byte_bytearray(randrange(1200, 24000)))

        # Request for load current
        elif rx_request == RequestCodes.load_current:
            # Load current returned is x100. 2 bytes. 0.00A to 30.00A.
            self.send(get_two_byte_bytearray(randrange(0, 3000)))

        # Request for load voltage
        elif rx_request == RequestCodes.load_voltage:
            # Load current returned is x100. 2 bytes. 10.00V to 20.00V.
            self.send(get_two_byte_bytearray(randrange(0, 2000)))

        # Request for load power
        elif rx_request == RequestCodes.load_power:
            # Load power returned is x100. 4 bytes. 0.00W to 360.00W.
            self.send(get_four_byte_bytearray(randrange(0, 36000)))

        # Request for battery status.
        elif rx_request == RequestCodes.batt_status:
            # Build 2 bytes to return, bit by bit.
            # Build response byte 0.
            byte0_bits0_3 = randint(0, 3)           # bits 0-3: in range 0-3
            byte0_bits4_7 = (randint(0, 2) << 4)    # bits 4-7: in range 0-2

            # Build response byte 1.
            byte1_bit8 = randint(0, 1)              # bit 8: boolean
            byte1_bit15 = randint(0, 1)             # bit 15: boolean

            # Make each byte
            byte0 = byte0_bits0_3 | byte0_bits4_7
            byte1 = byte1_bit8 | byte1_bit15
            # print "byte0: 0x%x, byte1: 0x%x" % (byte0, byte1)

            self.send(get_two_byte_bytearray(byte0 | (byte1 << 8)))

        # Request for charging equipment status.
        elif rx_request == RequestCodes.charging_equip_status:
            def randbool():
                return randint(0, 1)

            # Build 2 bytes to return, bit by bit.
            # Build response byte 0.
            byte0_bit0 = randbool()                 # bit 0: boolean
            byte0_bit1 = randbool() << 1            # bit 1: boolean
            byte0_bits2_3 = randrange(0, 2) << 2    # bits 2-3: in range 0-2
            byte0_bit4 = randbool() << 4            # bit 4: boolean
            byte0_bit7 = randbool() << 7            # bit 7: boolean

            # Build response byte 1.
            byte1_bit0 = randbool()                 # bit 0: boolean
            byte1_bit1 = randbool() << 1            # bit 1: boolean
            byte1_bit2 = randbool() << 2            # bit 2: boolean
            byte1_bit3 = randbool() << 3            # bit 3: boolean
            byte1_bit4 = randbool() << 4            # bit 4: boolean
            byte1_bit5 = randbool() << 5            # bit 5: boolean
            byte1_bits6_7 = randrange(0, 3) << 6    # bits 6-7: in range 0-3

            # Make each byte.
            byte0 = byte0_bit0 | byte0_bit1 | byte0_bits2_3 | byte0_bit4 | byte0_bit7
            byte1 = byte1_bit0 | byte1_bit1 | byte1_bit2 | byte1_bit3 | byte1_bit4 | byte1_bit5 | byte1_bits6_7
            # print "byte0: 0x%x, byte1: 0x%x" % (byte0, byte1)

            self.send(get_two_byte_bytearray(byte0 | (byte1 << 8)))

        # Exit the run() method and terminate.
        print "MockTracer exiting"

    def send(self, tx_data):
        """ Write response data back to the driver. """
        # Allow minimalmodbus to put the final response together for us, adding the crc.
        resp = minimalmodbus._embedPayload(1, MODE_RTU, 4, '%s' % tx_data)
        # Send response.
        print "MockTracer send: %s (%d)" % (resp, os.write(self.fd, resp))
