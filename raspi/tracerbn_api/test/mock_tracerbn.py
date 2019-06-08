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


class RequestCodes:
    """ Raw modbus request codes. One for each test run. """
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
    pv_voltage = bytearray([0x01, 0x04, 0x31, 0x00, 0x00, 0x01, 0x3F, 0x36])
    pv_current = bytearray([0x01, 0x04, 0x31, 0x01, 0x00, 0x01, 0x6E, 0xF6])
    pv_power = bytearray([0x01, 0x04, 0x31, 0x02, 0x00, 0x02, 0xDE, 0xF7])
    pv_voltage_max_today = bytearray([0x01, 0x04, 0x33, 0x00, 0x00, 0x01, 0x3E, 0x8E])
    pv_voltage_min_today = bytearray([0x01, 0x04, 0x33, 0x01, 0x00, 0x01, 0x6F, 0x4E])
    night_day = bytearray([0x01, 0x02, 0x20, 0x0C, 0x00, 0x01, 0x72, 0x09])
    energy_today = bytearray([0x01, 0x04, 0x33, 0x0C, 0x00, 0x02, 0xBE, 0x8C])
    energy_month = bytearray([0x01, 0x04, 0x33, 0x0E, 0x00, 0x02, 0x1F, 0x4C])
    energy_year = bytearray([0x01, 0x04, 0x33, 0x10, 0x00, 0x02, 0x7F, 0x4A])
    energy_total = bytearray([0x01, 0x04, 0x33, 0x12, 0x00, 0x02, 0xDE, 0x8A])
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
    """ This acts as a poor mans TracerBN emulator. It runs in a separate thread.
        When it receives a modbus request, it services the request with a sensible
        response.
        It may service a single request and exit, or service several
        requests then exit.
    """

    def __init__(self, fd):
        threading.Thread.__init__(self)
        self.fd = fd
        self.num_of_requests = 1
        print "MockTracer created"

    def run(self):
        """ Service 'num_of_requests' number of requests. """

        print "MockTracer running"

        while self.num_of_requests:

            rx_request = os.read(self.fd, 1024)
            print "MockTracer rcvd: " + rx_request

            # Request for device information.
            if rx_request == RequestCodes.device_info:
                # Return a string containing 'Tracer', we read 62 bytes at the other end.
                tx_string = "1234xyx+_&^$#Tracer#xyx+_&^$#4321" \
                            "987654cvbnmjhytre235:OI*GS$$Rgg4("
                # Send string.
                self.send(tx_string)

            # Request to test read_long_tracer() signed value, 0dp.
            elif rx_request == RequestCodes.read_long_signed:
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

            # Request for battery voltage.
            elif rx_request == RequestCodes.batt_voltage:
                # Voltage returned is x100. 2 bytes. 0V to 655.35V.
                self.send_two_bytes(randrange(0, 65535))

            # Request for battery current.
            elif rx_request == RequestCodes.batt_current:
                # Current returned is x100. 4 bytes. -21474836.48A to 21474836.47A.
                self.send_four_bytes(randrange(-2147483648, 2147483647))

            # Request for battery power.
            elif rx_request == RequestCodes.batt_power:
                # Power returned is x100. 4 bytes. 0W to 655.35W.
                self.send_four_bytes(randrange(0, 65535))

            # Request for battery temperature.
            elif rx_request == RequestCodes.batt_temp:
                # Temperature returned is x100. 2 bytes -327.68 to 327.67 degC.
                self.send_two_bytes(randrange(-32768, 32767))

            # Request for battery soc.
            elif rx_request == RequestCodes.batt_soc:
                # SOC is returned as a percentage. 2 bytes. 0% to 65535%.
                self.send_two_bytes(randrange(0, 65535))

            # Request for battery max voltage today.
            elif rx_request == RequestCodes.batt_voltage_max_today:
                # Max voltage today returned is x100. 2 bytes. 0V to 655.35V.
                self.send_two_bytes(randrange(0, 65535))

            # Request for battery min voltage today.
            elif rx_request == RequestCodes.batt_voltage_min_today:
                # Min voltage today returned is x100. 2 bytes. 0V to 655.35V.
                self.send_two_bytes(randrange(0, 65535))

            # Request for rated battery voltage.
            elif rx_request == RequestCodes.batt_rated_voltage:
                # Rated voltage returned 'should' be one of 9 discrete V values x100. 2 bytes. 12V to 240V.
                self.send_two_bytes(randrange(1200, 24000))

            # Request for load current.
            elif rx_request == RequestCodes.load_current:
                # Load current returned is x100. 2 bytes. 0A to 655.35A.
                self.send_two_bytes(randrange(0, 65535))

            # Request for load voltage.
            elif rx_request == RequestCodes.load_voltage:
                # Load voltage returned is x100. 2 bytes. 0V to 655.35V.
                self.send_two_bytes(randrange(0, 65535))

            # Request for load power.
            elif rx_request == RequestCodes.load_power:
                # Load power returned is x100. 4 bytes. 0W to 42949672.95W.
                self.send_four_bytes(randrange(0, 4294967295))

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

            # Request for PV current.
            elif rx_request == RequestCodes.pv_current:
                # PV current returned is x100. 2 bytes. 0A to 655.35A.
                self.send_two_bytes(randrange(0, 65535))

            # Request for PV voltage.
            elif rx_request == RequestCodes.pv_voltage:
                # PV voltage returned is x100. 2 bytes. 0V to 655.35V.
                self.send_two_bytes(randrange(0, 65535))

            # Request for PV power.
            elif rx_request == RequestCodes.pv_power:
                # PV power returned is x100. 4 bytes. 0W to 42949672.95W.
                self.send_four_bytes(randrange(0, 4294967295))

            # Request for PV max voltage today.
            elif rx_request == RequestCodes.pv_voltage_max_today:
                # Max voltage today returned is x100. 2 bytes. 0V to 655.35V.
                self.send_two_bytes(randrange(0, 65535))

            # Request for PV min voltage today.
            elif rx_request == RequestCodes.pv_voltage_min_today:
                # Min voltage today returned is x100. 2 bytes. 0V to 655.35V.
                self.send_two_bytes(randrange(0, 65535))

            # Request night / day status.
            elif rx_request == RequestCodes.night_day:
                # Night / day status returned as a boolean. 2 bytes.
                self.send_one_byte(randrange(0, 1), functioncode=2)

            # Request energy today.
            elif rx_request == RequestCodes.energy_today:
                # Energy today returned is x100. 4 bytes. 0.00kWhrs to 42949672.95kWhrs.
                self.send_four_bytes(randrange(0, 4294967295))

            # Request energy this month.
            elif rx_request == RequestCodes.energy_month:
                # Energy this month returned is x100. 4 bytes. 0.00kWhrs to 42949672.95kWhrs.
                self.send_four_bytes(randrange(0, 4294967295))

            # Request energy this year.
            elif rx_request == RequestCodes.energy_year:
                # Energy this year returned is x100. 4 bytes. 0.00kWhrs to 42949672.95kWhrs.
                self.send_four_bytes(randrange(0, 4294967295))

            # Request for energy total.
            elif rx_request == RequestCodes.energy_total:
                # Energy total returned is x100. 4 bytes. 0.00kWhrs to 42949672.95kWhrs.
                self.send_four_bytes(randrange(0, 4294967295))

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
            self.num_of_requests = self.num_of_requests - 1

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


if __name__ == "__main__":
    pid = os.getpid()
    # Get new pty master slave ends.
    fd_m, fd_s = pty.openpty()
    fd_m_path = os.readlink("/proc/%s/fd/%s" % (pid, fd_m))
    fd_s_path = os.readlink("/proc/%s/fd/%s" % (pid, fd_s))

    print("Starting MockTracerBN on fd: %s, %s, connect to %s" % (fd_m, fd_m_path, fd_s_path))
    mock_tracer = MockTracerBN(fd=fd_m)
    mock_tracer.num_of_requests = 10
    mock_tracer.run()           # Don't start thread.

    print("Exiting MockTracerBN")
