#!/usr/bin/python

__author__ = "James Park"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"

import tracerbn
import time
from flask import Flask

app = Flask(__name__)
serial_port = None


#
# Battery info
#
@app.route('/batt_voltage')
def batt_voltage():
    return "%s" % tracerbn.TracerBN(portname=serial_port).get_batt_voltage()


@app.route('/batt_current')
def batt_current():
    return "%s" % tracerbn.TracerBN(portname=serial_port).get_batt_current()


@app.route('/batt_power')
def batt_power():
    return "%s" % tracerbn.TracerBN(portname=serial_port).get_batt_power()


@app.route('/batt_temperature')
def batt_temperature():
    return "%s" % tracerbn.TracerBN(portname=serial_port).get_batt_temp()



#
# PV info
#
@app.route('/pv_voltage')
def pv_voltage():
    return "%s" % tracerbn.TracerBN(portname=serial_port).get_pv_voltage()


@app.route('/pv_current')
def pv_current():
    return "%s" % tracerbn.TracerBN(portname=serial_port).get_pv_current()


@app.route('/pv_power')
def pv_power():
    return "%s" % tracerbn.TracerBN(portname=serial_port).get_pv_power()


#
# Load info
#
@app.route('/load_voltage')
def load_voltage():
    return "%s" % tracerbn.TracerBN(portname=serial_port).get_load_voltage()


@app.route('/load_current')
def load_current():
    return "%s" % tracerbn.TracerBN(portname=serial_port).get_load_current()


@app.route('/load_power')
def load_power():
    return "%s" % tracerbn.TracerBN(portname=serial_port).get_load_power()


@app.route('/set_clock')
def set_clock():
    return "%s" % tracerbn.TracerBN(portname=serial_port).set_ctl_rtclock_localtime()


@app.route('/get_clock')
def get_clock():
    return time.strftime("%d %m %Y %H:%M:%S", tracerbn.TracerBN(portname=serial_port).get_ctl_rtclock_time())


#
# Controller info
#
@app.route('/night_day')
def night_or_day():
    return "%s" % tracerbn.TracerBN(portname=serial_port).get_night_or_day()


@app.route('/energy_total')
def energy_total():
    return "%s" % tracerbn.TracerBN(portname=serial_port).get_energy_total()


@app.route('/energy_year')
def energy_year():
    return "%s" % tracerbn.TracerBN(portname=serial_port).get_energy_year()


@app.route('/energy_month')
def energy_month():
    return "%s" % tracerbn.TracerBN(portname=serial_port).get_energy_month()


@app.route('/energy_day')
def energy_day():
    return "%s" % tracerbn.TracerBN(portname=serial_port).get_energy_today()


@app.route('/co2_saved')
def co2_saved():
    return "%s" % tracerbn.TracerBN(portname=serial_port).get_co2_saved()


if __name__ == '__main__':

    try:
        # Detect which serial port the TracerBN is connected to.
        serial_port = tracerbn.find_serial_port()
        app.run(debug=False, port=21001, host='0.0.0.0', threaded=False)
    except Exception as e:
        print "ERROR: Exiting: %s" % e

