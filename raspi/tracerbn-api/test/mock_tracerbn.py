#!/usr/bin/python

__author__ = "James Park"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"

import os
import pty
import threading
import minimalmodbus
from minimalmodbus import MODE_RTU
from random import randrange, randint
from mock_tracerbn_registers import registers


class RequestCodes:
    """ Raw modbus request codes. One for each test run. """
    batt_status = bytearray([0x01, 0x04, 0x32, 0x00, 0x00, 0x01, 0x3F, 0x72])
    batt_rated_voltage = bytearray([0x01, 0x04, 0x30, 0x04, 0x00, 0x01, 0x7F, 0x0B])
    charging_equip_status = bytearray([0x01, 0x04, 0x32, 0x01, 0x00, 0x01, 0x6E, 0xB2])
    co2_saved = bytearray([0x01, 0x04, 0x33, 0x14, 0x00, 0x02, 0x3E, 0x8B])
    clock_time_sec_min = bytearray([0x01, 0x03, 0x90, 0x13, 0x00, 0x01, 0x58, 0xCF])
    clock_time_hour_day = bytearray([0x01, 0x03, 0x90, 0x14, 0x00, 0x01, 0xE9, 0x0E])
    clock_time_month_year = bytearray([0x01, 0x03, 0x90, 0x15, 0x00, 0x01, 0xB8, 0xCE])

    # These addresses (9990 - 9992) are completely fictitious.
    # They are made up for the purposes of this general read test.
    read_long_signed = bytearray([0x01, 0x04, 0x99, 0x90, 0x00, 0x02, 0x5F, 0x7A])
    read_long_unsigned = bytearray([0x01, 0x04, 0x99, 0x91, 0x00, 0x02, 0x0E, 0xBA])
    read_long_signed_4dp = bytearray([0x01, 0x04, 0x99, 0x92, 0x00, 0x02, 0xFE, 0xBA])

    def __init__(self): pass


class MockTracerBN(threading.Thread):
    """ This acts as a poor mans TracerBN emulator. It can run as a thread.
        When it receives a modbus request, it services the request with a sensible
        response.
        It may service a finite number of requests and exit, or service an infinite number of requests.
    """

    def __init__(self, fd, num_responses=1):
        threading.Thread.__init__(self)
        self.fd = fd
        self._num_of_requests = num_responses
        self._registers = registers

    def run(self):
        """ Handle requests. """

        while self._num_of_requests != 0:

            rx_request = os.read(self.fd, 1024)
            print "MockTracer rcvd: " + rx_request

            for endpoint in self._registers:
                if rx_request == endpoint.request_code_array:
                    print "Request for '%s', returning value: '%s', len: %s" % (endpoint, endpoint.response, endpoint.response_byte_len)

                    if endpoint.response_byte_len > 4:
                        self.send(endpoint.response, functioncode=endpoint.function_code)

                    elif endpoint.response_byte_len == 4:
                        self.send_four_bytes(endpoint.response, functioncode=endpoint.function_code)

                    elif endpoint.response_byte_len == 2:
                        self.send_two_bytes(endpoint.response, functioncode=endpoint.function_code)

                    elif endpoint.response_byte_len == 1:
                        self.send_one_byte(endpoint.response, functioncode=endpoint.function_code)
                    else:
                        print "Error, endpoint response length 0 or < 0"
                        print "Error, not returning any respose from endpoint '%s'" % endpoint

            # Request to test read_long_tracer() signed value, 0dp.
            if rx_request == RequestCodes.read_long_signed:
                # Value returned is 4 bytes. -2147483648 to 2147483647.
                self.send_four_bytes(randrange(-2147483648, 2147483647))

            # Request to test read_long_tracer() un-signed value, 0dp..
            elif rx_request == RequestCodes.read_long_unsigned:
                # Value returned is 4 bytes. 0 to 4294967295.
                self.send_four_bytes(randrange(0, 4294967295))

            # Request to test read_long_tracer() signed value, 4dp..
            elif rx_request == RequestCodes.read_long_signed_4dp:
                # Value returned is 4 bytes. -2147483648, 2147483647.
                self.send_four_bytes(randrange(-2147483648, 2147483647))

            # Request for rated battery voltage.
            elif rx_request == RequestCodes.batt_rated_voltage:
                # Rated voltage returned 'should' be one of 9 discrete V values x100. 2 bytes. 12V to 240V.
                self.send_two_bytes(randrange(1200, 24000))

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

                self.send_two_bytes(byte0 | (byte1 << 8))

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

                self.send_two_bytes(byte0 | (byte1 << 8))

            # Request for CO2 saved.
            elif rx_request == RequestCodes.co2_saved:
                # CO2 saved returned is x100. 2 bytes. 0.00T to 655.35T.
                self.send_four_bytes(randrange(0, 4294967295))

            # Request for clock seconds and / or clock minutes.
            elif rx_request == RequestCodes.clock_time_sec_min:
                # Seconds returned is the low byte of a register. Minutes returned is the high byte of a register.
                # Use sensible vals it's strptime'd in the driver.
                sec = randrange(0, 59)
                min = randrange(0, 59) << 8
                self.send_two_bytes(sec | min, functioncode=3)

            # Request for clock hours and / or clock days.
            elif rx_request == RequestCodes.clock_time_hour_day:
                # Hours returned is the low byte of a register. Days returned is the high byte of a register.
                # Use sensible vals it's strptime'd in the driver.
                hour = randrange(0, 23)
                day = randrange(1, 31) << 8
                self.send_two_bytes(hour | day, functioncode=3)

            # Request for clock months and / or clock years.
            elif rx_request == RequestCodes.clock_time_month_year:
                # Months returned is the low byte of a register. Years returned is the high byte of a register.
                # Use sensible vals it's strptime'd in the driver.
                month = randrange(1, 12)
                year = randrange(0, 99) << 8
                self.send_two_bytes(month | year, functioncode=3)

            # Decrement our request counter.
            self._num_of_requests = self._num_of_requests - 1

        # Done. Exit the run() method and terminate.
        print "MockTracer exiting"

    #
    # Utility functions for sending various numbers of bytes.
    #
    def send_four_bytes(self, data, functioncode=4):
        """ Write 4 bytes of response data back to the driver. """
        byte0 = data & 0xFF
        byte1 = (data >> 8) & 0xFF
        byte2 = (data >> 16) & 0xFF
        byte3 = (data >> 24) & 0xFF
        # Note the byte order.
        self.send([4, byte1, byte0, byte3, byte2], functioncode)

    def send_two_bytes(self, data, functioncode=4):
        """ Write 2 bytes of response data back to the driver. """
        byte0 = data & 0xFF
        byte1 = (data >> 8) & 0xFF
        self.send([2, byte1, byte0], functioncode)

    def send_one_byte(self, data, functioncode=4):
        """ Write 1 byte of response data back to the driver. """
        byte0 = data & 0xFF
        self.send([1, byte0], functioncode)

    def send(self, tx_data, functioncode=4):
        """ Write response data back to the driver. """
        # Allow minimalmodbus to put the final response together for us, adding the crc.
        resp = minimalmodbus._embedPayload(1, MODE_RTU, functioncode, '%s' % bytearray(tx_data))
        # Send response.
        print "MockTracer send: %s (%d)" % (resp, os.write(self.fd, resp))


def create_symlink(src, dest):
    # Symlink the slave fd path to /dev/mock_tracerbn for consistency.
    try:
        if os.path.islink(dest):
            os.unlink(dest)
        os.symlink(src, dest)
    except OSError as e:
        print("Error, did not create symlink %s --> %s. Reason:" % (src, dest))
        print("     %s" % e)
    else:
        print("symlink '%s --> %s' created" % (src, dest))


if __name__ == "__main__":
    # This runs TracerBN as an emulator / simulator in place of the real thing.

    link_dest = '/dev/mock_tracerbn'
    pid = os.getpid()
    # Get new pty master slave ends.
    fd_m, fd_s = pty.openpty()
    fd_m_path = os.readlink("/proc/%s/fd/%s" % (pid, fd_m))
    fd_s_path = os.readlink("/proc/%s/fd/%s" % (pid, fd_s))

    # Create mock device and set to handle infinite requests.
    mock_tracer = MockTracerBN(fd=fd_m, num_responses=-1)

    print("Running MockTracerBN. Mock device available on %s" % fd_s_path)
    create_symlink(fd_s_path, link_dest)
    mock_tracer.run()           # Don't start() thread.

    # Delete symlink.
    # We assume we are root if the link exists, we must have created it.
    # Therefore no permissions check here.
    if os.path.islink(link_dest):
        print("removing symlink %s --> %s" % (fd_s_path, link_dest))
        os.unlink(link_dest)
    print("mock_tracerbn exited")
