#!/usr/bin/python

__author__ = "James Park"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"

from random import randrange, randint, uniform


class BaseRegister:
    def __init__(self, name, request_code_array, response=None, response_byte_len=None, function_code=4):
        self._name = name
        self.request_code_array = bytearray(request_code_array)
        self._response = response
        self.response_byte_len = response_byte_len
        self.function_code = function_code

    def __str__(self):
        return self._name


class Register(BaseRegister):

    def __init__(self, name, request_code_array, response=None, response_byte_len=None, response_meta_array=None, dp=None, function_code=4):
        BaseRegister.__init__(self, name, request_code_array, response, response_byte_len, function_code)

        self.response_meta_array = response_meta_array
        self._dp = dp

    @property
    def response(self):
        if self._response is None:

            # Generate response.
            low = int(self.response_meta_array[0])
            high = int(self.response_meta_array[1])

            if self._dp is not None and self._dp > 0:
                low = low * (10 ** self._dp)
                high = high * (10 ** self._dp)

            return randint(low, high)
        else:
            # pre-defined response, set the length and return
            self.response_byte_len = len(self._response)
            return self._response

    @response.setter
    def response(self, response):
        self._response = response


registers = [
    Register("Device Info",
             request_code_array=[0x01, 0x2b, 0x0e, 0x01, 0x00, 0x70, 0x77],
             response="1234xyx+_&^$#Tracer#xyx+_&^$#4321987654cvbnmjhytre235:OI*GS$$Rgg4(",
             function_code=2
             ),
    Register("Battery Voltage",
             request_code_array=[0x01, 0x04, 0x33, 0x1A, 0x00, 0x01, 0x1F, 0x49],
             response_byte_len=2,
             response_meta_array=[0, 15],
             dp=2
             ),
    Register("Battery Current",
             request_code_array=[0x01, 0x04, 0x33, 0x1B, 0x00, 0x02, 0x0E, 0x88],
             response_byte_len=4,
             response_meta_array=[-10, 10],
             dp=2
             ),
    Register("Battery Power",
             request_code_array=[0x01, 0x04, 0x31, 0x06, 0x00, 0x02, 0x9F, 0x36],
             response_byte_len=4,
             response_meta_array=[-50, 50],
             dp=2
             ),
    Register("Battery Temperature",
             request_code_array=[0x01, 0x04, 0x31, 0x1B, 0x00, 0x01, 0x4F, 0x31],
             response_byte_len=2,
             response_meta_array=[-50, 100],
             dp=2
             ),
    Register("Battery State of Charge",
             request_code_array=[0x01, 0x04, 0x31, 0x1A, 0x00, 0x01, 0x1E, 0xF1],
             response_byte_len=2,
             response_meta_array=[0, 100],
             dp=2
             ),
    Register("Battery Voltage Max Today",
             request_code_array=[0x01, 0x04, 0x33, 0x02, 0x00, 0x01, 0x9F, 0x4E],
             response_byte_len=2,
             response_meta_array=[0, 20],
             dp=2
             ),
    Register("Battery Voltage Min Today",
             request_code_array=[0x01, 0x04, 0x33, 0x03, 0x00, 0x01, 0xCE, 0x8E],
             response_byte_len=2,
             response_meta_array=[0, 20],
             dp=2
             ),
    Register("Load Current",
             request_code_array=[0x01, 0x04, 0x31, 0x0D, 0x00, 0x01, 0xAE, 0xF5],
             response_byte_len=2,
             response_meta_array=[0, 50],
             dp=2
             ),
    Register("Load Voltage",
             request_code_array=[0x01, 0x04, 0x31, 0x0C, 0x00, 0x01, 0xFF, 0x35],
             response_byte_len=2,
             response_meta_array=[0, 20],
             dp=2
             ),
    Register("Load Power",
             request_code_array=[0x01, 0x04, 0x31, 0x0E, 0x00, 0x02, 0x1E, 0xF4],
             response_byte_len=4,
             response_meta_array=[0, 250],
             dp=2
             ),
    Register("PV Current",
             request_code_array=[0x01, 0x04, 0x31, 0x01, 0x00, 0x01, 0x6E, 0xF6],
             response_byte_len=2,
             response_meta_array=[0, 50],
             dp=2
             ),
    Register("PV Voltage",
             request_code_array=[0x01, 0x04, 0x31, 0x00, 0x00, 0x01, 0x3F, 0x36],
             response_byte_len=2,
             response_meta_array=[0, 20],
             dp=2
             ),
    Register("PV Power",
             request_code_array=[0x01, 0x04, 0x31, 0x02, 0x00, 0x02, 0xDE, 0xF7],
             response_byte_len=4,
             response_meta_array=[0, 250],
             dp=2
             ),
    Register("PV Voltage Max Today",
             request_code_array=[0x01, 0x04, 0x33, 0x00, 0x00, 0x01, 0x3E, 0x8E],
             response_byte_len=2,
             response_meta_array=[0, 20],
             dp=2
             ),
    Register("PV Voltage Min Today",
             request_code_array=[0x01, 0x04, 0x33, 0x01, 0x00, 0x01, 0x6F, 0x4E],
             response_byte_len=2,
             response_meta_array=[0, 20],
             dp=2
             ),
    Register("Generated Energy Today",
             request_code_array=[0x01, 0x04, 0x33, 0x0C, 0x00, 0x02, 0xBE, 0x8C],
             response_byte_len=4,
             response_meta_array=[0, 2000],
             dp=2
             ),
    Register("Generated Energy this Month",
             request_code_array=[0x01, 0x04, 0x33, 0x0E, 0x00, 0x02, 0x1F, 0x4C],
             response_byte_len=4,
             response_meta_array=[0, 2000],
             dp=2
             ),
    Register("Generated Energy this Year",
             request_code_array=[0x01, 0x04, 0x33, 0x10, 0x00, 0x02, 0x7F, 0x4A],
             response_byte_len=4,
             response_meta_array=[0, 2000],
             dp=2
             ),
    Register("Generated Energy Total",
             request_code_array=[0x01, 0x04, 0x33, 0x12, 0x00, 0x02, 0xDE, 0x8A],
             response_byte_len=4,
             response_meta_array=[0, 2000],
             dp=2
             ),
    Register("Night / Day",
             request_code_array=[0x01, 0x02, 0x20, 0x0C, 0x00, 0x01, 0x72, 0x09],
             response_byte_len=1,
             response_meta_array=[0, 1],
             dp=0,
             function_code=2
             )
]
