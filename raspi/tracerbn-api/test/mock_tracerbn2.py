#!/usr/bin/python3
# from __builtin__ import type
from pymodbus.server.sync import ModbusSerialServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSparseDataBlock, ModbusSequentialDataBlock
from pymodbus.transaction import ModbusRtuFramer
from collections import defaultdict
import json
import os
import threading
import logging

# Grab a logger
log = logging.getLogger()

# json file should be in the same directory as this file
DEVICE_JSON_DESC_PATH = '%s/mock_tracerbn_reg_map.json' % os.path.dirname(os.path.abspath(__file__))

class MockTracerBN2(threading.Thread):

    def __init__(self, serial_port='/dev/pts/4', json_device_desc_path=DEVICE_JSON_DESC_PATH):
        threading.Thread.__init__(self, name='MockTracerBN2')
        self._serial_port = serial_port

        # Build data backing store from json file.
        mappings = json_mapping_parser(json_device_desc_path)
        store = ModbusSlaveContext(
            di = ModbusSparseDataBlock(mappings['di']),
            co = ModbusSparseDataBlock(mappings['co']),
            ir = ModbusSparseDataBlock(mappings['ir']),
            hr = ModbusSparseDataBlock(mappings['hr'])
        )
        identity = initialise_device_identity(mappings)
        context = ModbusServerContext(slaves=store, single=True)

        # RTU:
        self.server = ModbusSerialServer(context,
                                         framer=ModbusRtuFramer,
                                         identity=identity,
                                         port=self._serial_port,
                                         timeout=0.001,
                                         baudrate=115200
                                         )

    def run(self):
        self.server.serve_forever()

    def stop(self):
        if self.server.is_running:
            self.server.server_close()
            del self.server


def initialise_device_identity(mappings=None):
    """ Initialise device identity (MEI) using information
    from supplied mappings if available.

    :param mappings: dict of device information
    :return: initialised ModbusDeviceIdentification object
    """
    identity = ModbusDeviceIdentification()
    if mappings.get('identity', False):
        ident_data = dict(mappings.get('identity'))

        identity.VendorName = ident_data.get('vendorname')
        identity.ProductCode = ident_data.get('productcode')
        identity.VendorUrl = ident_data.get('vendorurl')
        identity.ProductName = ident_data.get('productname')
        identity.ModelName = ident_data.get('modelname')
        identity.MajorMinorRevision = ident_data.get('majorminorrevision')

    return identity


# --------------------------------------------------------------------------- #
# raw mapping input parsers
# --------------------------------------------------------------------------- #
def json_mapping_parser(path):
    """ Given a json file of the the mapping data for
    a modbus device, return a mapping layout that can
    be used to decode an new block.

    :param path: The path to the csv input file
    :returns: The decoded json dictionary
    """

    mappings = defaultdict(lambda: [0x00] * 65536)  # Return empty address space by default (when key not present)
    offset = 1

    try:
        with open(path, 'r') as handle:
            input_data = json.load(handle)
            device = input_data["device"]

            for reg_type in device:

                # Deal with identity (MEI) registers in this block
                if reg_type in ['identity']:
                    mappings['identity'] = {ident_attr: v for ident_attr, v in device[reg_type].items()}
                    continue

                # Deal with data registers in this block
                for reg in device[reg_type]:
                    # Log and exit quick if not correctly defined
                    if not reg.get('address', False):
                        log.warn("Skipping register. Address or Value not defined for register '%s'" % reg)
                        continue

                    values = []
                    i = 0

                    # Deal with hex or int address types:
                    a = reg.get('address')
                    address = int(a) if type(a) == int else int(a, 16)

                    # Apply scaling.
                    v = int(reg.get('value') * reg.get('scale', 1))   # if no scaling attribute found default to 1.

                    # Deal with values which have size > 16 bits.
                    if reg.get('length', 1) is 1:                       # if no length attribute found, default to 1.
                        values.append(v)
                    elif reg.get('length') == 2:
                        values.append(v & 0x0000FFFF)
                        values.append((v & 0xFFFF0000) >> 16)
                    else:
                        raise(Exception("can't handle data length > 2 bytes !"))

                    # Store register address-value mappings
                    for v in values:
                        log.debug("reg: %s, %s, v: %s" % (reg_type, reg.get('name'), v))
                        mappings[reg_type][address + offset + i] = v
                        i += 1

    except Exception as e:
        log.error("json_mapping_parser Failed to load json description file %s" % path)
        log.error("json_mapping_parser Exception was: %s" % e)
        raise e

    return mappings


# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    mock_tracerbn = MockTracerBN2()
    # mock_tracerbn.start()
