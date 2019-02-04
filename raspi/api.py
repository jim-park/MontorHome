#!/usr/bin/python

__author__ = "James Park"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"

import tracerbn
from flask import Flask

app = Flask(__name__)

#
# Battery info
#
@app.route('/batt_voltage')
def batt_voltage():
    return "%s" % tracerbn.TracerBN().get_batt_voltage()


@app.route('/batt_current')
def batt_current():
    return "%s" % tracerbn.TracerBN().get_batt_current()


@app.route('/batt_temperature')
def batt_temperature():
    return "%s" % tracerbn.TracerBN().get_batt_temp()


#
# PV info
#
@app.route('/pv_voltage')
def pv_voltage():
    return "%s" % tracerbn.TracerBN().get_pv_voltage()


@app.route('/pv_current')
def pv_current():
    return "%s" % tracerbn.TracerBN().get_pv_current()


@app.route('/pv_power')
def pv_power():
    return "%s" % tracerbn.TracerBN().get_pv_power()


#
# Load info
#
@app.route('/load_voltage')
def load_voltage():
    return "%s" % tracerbn.TracerBN().get_load_voltage()


@app.route('/load_current')
def load_current():
    return "%s" % tracerbn.TracerBN().get_load_current()


@app.route('/load_power')
def load_power():
    return "%s" % tracerbn.TracerBN().get_load_power()


if __name__ == '__main__':
    app.run(debug=False, port=21001, host='0.0.0.0', threaded=False)
