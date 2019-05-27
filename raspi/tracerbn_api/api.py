#!/usr/bin/env python

__author__ = "James Park"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"

import tracerbn
import time
from flask import Flask
import json
from prometheus_client import Gauge, Summary, start_http_server, make_wsgi_app
from werkzeug.wsgi import DispatcherMiddleware
app = Flask(__name__)
serial_port = None

batt_soc_gauge = Gauge('battery_state_of_charge_percentage', "Battery SOC as a percentage")
batt_volt_gauge = Gauge('battery_voltage_volts', "Battery voltage in Volts")
batt_power_gauge = Gauge('battery_power_watts', "Battery power in Watts")
batt_curr_gauge = Gauge('battery_current_amperes', "Battery current in Amperes")
pv_volt_gauge = Gauge('pv_voltage_volts', "PV voltage in Volts")
pv_power_gauge = Gauge('pv_power_watts', "PV power in Watts")
pv_curr_gauge = Gauge('pv_current_amperes', "PV current in Amperes")

def safe_tracer():
    global serial_port
    retries = 3

    while retries > 0:
        try:
            return tracerbn.TracerBN(portname=serial_port)
        except Exception as e:
            print "ERROR: %s" % e
            print "ERROR: Searching ports for TracerBN ..."
            serial_port = tracerbn.find_serial_port()
        retries = retries - 1

    # If we've reached here we've failed. Exit and let supervisor restart us.
    exit(-1)

app_dispatch = DispatcherMiddleware(app, {
  '/metrics': make_wsgi_app()
})

#
# Battery info
#
@app.route('/batt_voltage')
def batt_voltage():
    global batt_volt_gauge
    tmp = safe_tracer().get_batt_voltage()
    batt_volt_gauge.set(tmp)
    return "%s" % tmp

@app.route('/batt_voltage_max')
def batt_voltage_max():
    return "%s" % safe_tracer().get_batt_voltage_max_today()


@app.route('/batt_voltage_min')
def batt_voltage_min():
    return "%s" % safe_tracer().get_batt_voltage_min_today()


@app.route('/batt_current')
def batt_current():
    global batt_curr_gauge
    tmp = safe_tracer().get_batt_current()
    batt_curr_gauge.set(tmp)
    return "%s" % tmp


@app.route('/batt_power')
def batt_power():
    global batt_power_gauge
    tmp = safe_tracer().get_batt_power()
    batt_power_gauge.set(tmp)
    return "%s" % tmp


@app.route('/batt_temperature')
def batt_temperature():
    return "%s" % safe_tracer().get_batt_temp()


@app.route('/batt_soc')
def batt_soc():
    global batt_soc_gauge
    tmp = safe_tracer().get_batt_soc()
    batt_soc_gauge.set(tmp)
    return "%s" % tmp


@app.route('/batt_status')
def batt_status():
    return "%s" % json.dumps(safe_tracer().get_batt_status())


@app.route('/batt_rated_capacity')
def batt_rated_capacity():
    return "%s" % safe_tracer().get_batt_rated_capacity()


@app.route('/batt_rated_voltage')
def batt_rated_voltage():
    return "%s" % safe_tracer().get_batt_rated_voltage()



#
# PV info
#
@app.route('/pv_voltage')
def pv_voltage():
    global pv_volt_gauge
    tmp = safe_tracer().get_pv_voltage()
    pv_volt_gauge.set(tmp)
    return "%s" % tmp


@app.route('/pv_voltage_max')
def pv_voltage_max():
    return "%s" % safe_tracer().get_pv_voltage_max_today()


@app.route('/pv_voltage_min')
def pv_voltage_min():
    return "%s" % safe_tracer().get_pv_voltage_min_today()


@app.route('/pv_current')
def pv_current():
    global pv_curr_gauge
    tmp = safe_tracer().get_pv_current()
    pv_curr_gauge.set(tmp)
    return "%s" % tmp


@app.route('/pv_power')
def pv_power():
    global pv_power_gauge
    tmp = safe_tracer().get_pv_power()
    pv_power_gauge.set(tmp)
    return "%s" % tmp


#
# Load info
#
@app.route('/load_voltage')
def load_voltage():
    return "%s" % safe_tracer().get_load_voltage()


@app.route('/load_current')
def load_current():
    return "%s" % safe_tracer().get_load_current()


@app.route('/load_power')
def load_power():
    return "%s" % safe_tracer().get_load_power()


#
# Controller clock.
#
@app.route('/set_clock')
def set_clock():
    return "%s" % safe_tracer().set_ctl_rtclock_localtime()


@app.route('/get_clock')
def get_clock():
    return time.strftime("%d %m %Y %H:%M:%S", safe_tracer().get_ctl_rtclock_time())


#
# Controller info
#
@app.route('/night_day')
def night_or_day():
    return "%s" % safe_tracer().get_night_or_day()


@app.route('/energy_total')
def energy_total():
    return "%s" % safe_tracer().get_energy_total()


@app.route('/energy_year')
def energy_year():
    return "%s" % safe_tracer().get_energy_year()


@app.route('/energy_month')
def energy_month():
    return "%s" % safe_tracer().get_energy_month()


@app.route('/energy_day')
def energy_day():
    return "%s" % safe_tracer().get_energy_today()


@app.route('/co2_saved')
def co2_saved():
    return "%s" % safe_tracer().get_co2_saved()


@app.route('/charging_equip_status')
def charging_equip_status():
    return "%s" % json.dumps(safe_tracer().get_charging_equip_status())



if __name__ == '__main__':

    try:
        # Detect which serial port the TracerBN is connected to.
        serial_port = tracerbn.find_serial_port()
        start_http_server(8000)
        app.run(debug=False, port=21001, host='0.0.0.0', threaded=False)
    except Exception as e:
        print "ERROR: Exiting: %s" % e

