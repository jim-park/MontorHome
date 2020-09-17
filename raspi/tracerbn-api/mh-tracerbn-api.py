#!/usr/bin/env python3

__author__ = "James Park"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"

import time
from flask import Flask
import json

from mhtracerbn import find_serial_port, TracerBN

# Initialise app and TracerBN connection
app = Flask(__name__)
serial_port = find_serial_port()     # Will raise exception if no serial port found
device = TracerBN(portname=serial_port)


#
# Battery info
#
@app.route('/batt_voltage')
def batt_voltage():
    return "%s" % device.get_batt_voltage()


@app.route('/batt_voltage_max')
def batt_voltage_max():
    return "%s" % device.get_batt_voltage_max_today()


@app.route('/batt_voltage_min')
def batt_voltage_min():
    return "%s" % device.get_batt_voltage_min_today()


@app.route('/batt_current')
def batt_current():
    return "%s" % device.get_batt_current()


@app.route('/batt_power')
def batt_power():
    return "%s" % device.get_batt_power()


@app.route('/batt_temperature')
def batt_temperature():
    return "%s" % device.get_batt_temp()


@app.route('/batt_soc')
def batt_soc():
    return "%s" % device.get_batt_soc()


@app.route('/batt_status')
def batt_status():
    return "%s" % json.dumps(device.get_batt_status())


@app.route('/batt_rated_capacity')
def batt_rated_capacity():
    return "%s" % device.get_batt_rated_capacity()


@app.route('/batt_rated_voltage')
def batt_rated_voltage():
    return "%s" % device.get_batt_rated_voltage()


#
# PV info
#
@app.route('/pv_voltage')
def pv_voltage():
    return "%s" % device.get_pv_voltage()


@app.route('/pv_voltage_max')
def pv_voltage_max():
    return "%s" % device.get_pv_voltage_max_today()


@app.route('/pv_voltage_min')
def pv_voltage_min():
    return "%s" % device.get_pv_voltage_min_today()


@app.route('/pv_current')
def pv_current():
    return "%s" % device.get_pv_current()


@app.route('/pv_power')
def pv_power():
    return "%s" % device.get_pv_power()


#
# Load info
#
@app.route('/load_voltage')
def load_voltage():
    return "%s" % device.get_load_voltage()


@app.route('/load_current')
def load_current():
    return "%s" % device.get_load_current()


@app.route('/load_power')
def load_power():
    return "%s" % device.get_load_power()


#
# Controller clock.
#
@app.route('/set_clock')
def set_clock():
    return "%s" % device.set_ctl_rtclock_localtime()


@app.route('/get_clock')
def get_clock():
    return time.strftime("%d %m %Y %H:%M:%S", device.get_ctl_rtclock_time())


#
# Controller info
#
@app.route('/night_day')
def night_or_day():
    return "%s" % device.get_night_or_day()


@app.route('/energy_total')
def energy_total():
    return "%s" % device.get_energy_total()


@app.route('/energy_year')
def energy_year():
    return "%s" % device.get_energy_year()


@app.route('/energy_month')
def energy_month():
    return "%s" % device.get_energy_month()


@app.route('/energy_day')
def energy_day():
    return "%s" % device.get_energy_today()


@app.route('/co2_saved')
def co2_saved():
    return "%s" % device.get_co2_saved()


@app.route('/charging_equip_status')
def charging_equip_status():
    return "%s" % json.dumps(device.get_charging_equip_status())


if __name__ == '__main__':
    app.run(debug=False, port=21001, host='0.0.0.0', threaded=False)
