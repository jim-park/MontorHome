#!/usr/bin/env python

import os
import time
import signal
import urllib
import pprint
from influxdb import InfluxDBClient
import ConfigParser

# Get and assign os environment vars.
# log_status_period = float(os.getenv('LOG_STATUS_PERIOD', 1800))
# api_url = os.getenv('API_URL')
# api_http_port = os.getenv('API_HTTP_PORT')
# api_fetch_period = float(os.getenv('API_FETCH_PERIOD'))
# db_host = os.getenv('DB_HOST')
# db_port = os.getenv('DB_PORT')
# db_name = os.getenv('DB_NAME')
# endpoints_env = [i for i in os.environ.get("ENDPOINTS").split(" ")]
#
# # Make endpoints dict from endpoints env var.
# endpoints = dict()
# for ep in endpoints_env:
#     endpoints[ep] = None


# CONFIG_FILE_PATH = '/etc/mh-data-acquisition.conf'
CONFIG_FILE_PATH = '/etc/mh-data-acquisition.conf'

# Initialise config.
config = ConfigParser.SafeConfigParser()
config.read(CONFIG_FILE_PATH)

# Load config
api_url = config.get("default", 'api_url')
log_status_period = config.getfloat("default", 'log_status_period')
api_http_port = config.getint("default", 'api_http_port')
api_fetch_period = config.getfloat("default", 'api_fetch_period')
db_host = config.get("default", 'db_host')
db_port = config.getint("default", 'db_port')
db_name = config.get("default", 'db_name')
endpoints_list = [i for i in config.get("default", 'endpoints').split("\n")]
# Pythonic creation of a dict of endpoints.
# Keys are endpoint names, values are initialised to None.
endpoints = dict(zip(endpoints_list[::1], [None for l in endpoints_list]))

print "loaded config:\n" \
      "\t'log status period'    : '%s'\n" \
      "\t'api url'              : '%s'\n" \
      "\t'api http port'        : '%s'\n" \
      "\t'api fetch period'     : '%s'\n" \
      "\t'db host'              : '%s'\n" \
      "\t'db port'              : '%s'\n" \
      "\t'db name'              : '%s'\n" \
      "\t'endpoints'            : '%s'\n" \
      % (log_status_period, api_url, api_http_port, api_fetch_period,
         db_host, db_port, db_name, endpoints_list)

# Global vars.
db_client = None
running = True


# Signal handler.
def handler(a, b):  # define the handler
    print("Caught SIGINT signal. Shutting down")
    global running
    running = False


# Connect to InfluxDB
def db_connect():
    global db_client

    try:
        db_client = InfluxDBClient(host=db_host, port=db_port)
        if db_name not in [v['name'] for v in db_client.get_list_database()]:
            db_client.create_database(db_name)
            print("Database: %s created on host %s" % (db_name, db_host))
        db_client.switch_database(db_name)

    except Exception as e:
        print("Failed to connect to DB")
        raise e
    else:
        print("Connected to DB OK")


# Main run loop
def main():
    global running

    json_body = [{
        "measurement": "fast_data",
        "fields": {}
    }]

    # Timer used for periodic log output only.
    now = time.time() - log_status_period
    counter = 0

    try:
        db_connect()
        while running:

            #
            # Fetch data from all endpoints.
            #
            for endpoint in endpoints.keys():

                url = "%s:%s/%s" % (api_url, api_http_port, endpoint)
                f = urllib.urlopen(url)
                endpoints[endpoint] = float(f.read())

                counter = counter + 1

            #
            # Format data for db.
            #
            json_body[0]['fields'] = endpoints
            #print "json_body[fields]: %s" % json_body[0]['fields']

            #
            # Insert data into db
            #
            # pprint.pprint(json_body)
            db_client.write_points(json_body)

            # Log for reassurance.
            if time.time() - now > log_status_period:
                print("stored %s records" % counter)
                now = time.time()

            # Wait for the next time ...
            time.sleep(api_fetch_period)

    except Exception as e:
        print(e)
        print("Caught Exception, Exiting")
        running = False

    finally:
        print("closing db client conn")
        db_client.close()


if __name__ == "__main__":
    print("Started")
    signal.signal(signal.SIGINT, handler)  # assign the handler to the signal SIGINT
    main()
    print("Exited")
