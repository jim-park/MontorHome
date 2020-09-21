#!/usr/bin/env python3

import time
import signal
import urllib.request
import requests
import logging
from influxdb import InfluxDBClient
from configparser import ConfigParser

# Global vars.
# CONFIG_FILE_PATH = './mh-data-acquisition.conf'     # For dev
CONFIG_FILE_PATH = '/etc/mh-data-acquisition.conf'
db_client = None
running = True

# Initialise config.
config = ConfigParser()
config.read(CONFIG_FILE_PATH)

# Read and assign config
api_url = config.get("default", 'api_url')
log_file_path = config.get("default", 'log_file_path')
log_level = config.get("default", "log_level")
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

# Initialise and setup logger
log = logging.getLogger('mh-logger')
log.setLevel(log_level)
handler = logging.FileHandler(log_file_path)
log.addHandler(handler)
# Create and add logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Dump config
log.info("loaded config:\n" \
      "\t'log file path'        : '%s'\n" \
      "\t'log status period'    : '%s'\n" \
      "\t'api url'              : '%s'\n" \
      "\t'api http port'        : '%s'\n" \
      "\t'api fetch period'     : '%s'\n" \
      "\t'db host'              : '%s'\n" \
      "\t'db port'              : '%s'\n" \
      "\t'db name'              : '%s'\n" \
      "\t'endpoints'            : '%s'" \
      % (log_file_path, log_status_period, api_url, api_http_port, api_fetch_period,
         db_host, db_port, db_name, endpoints_list)
      )


# Signal handler.
def handler(a, b):  # define the handler
    log.info("Caught SIGTERM signal. Shutting down")
    global running
    running = False


# Connect to InfluxDB
def db_connect():
    global db_client
    db_connected = False
    # TODO - make hardcoded values configurable items
    retry_wait_secs = 10
    max_retries = 5
    retry_counter = max_retries

    while not db_connected and retry_counter > 0:
        try:
            db_client = InfluxDBClient(host=db_host, port=db_port)
            if db_name not in [v['name'] for v in db_client.get_list_database()]:
                db_client.create_database(db_name)
                log.debug("Database: %s created on host %s" % (db_name, db_host))
            db_client.switch_database(db_name)

        except requests.exceptions.ConnectionError as e:
            log.error("ConnectionError exception connecting to DB ... still starting up?")
            retry_counter -= 1

            # Too many retry attempts, exit
            if retry_counter <= 0:
                log.warning("DB connection retries (%d) exceeded, giving up" % max_retries)
                raise e

            # We're probably just starting up, so wait a while ...
            time.sleep(retry_wait_secs)

        except Exception as e:
            log.error("Unhandled Exception connecting to DB.")
            log.exception(e)
            raise e
        else:
            db_connected = True
            log.info("Connected to DB OK")


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
                try:
                    f = urllib.request.urlopen("%s:%s/%s" % (api_url, api_http_port, endpoint))
                except ConnectionError as e:
                    log.error("Exception connecting to API.")
                    log.error("e: %s" % str(e))
                    raise e
                endpoints[endpoint] = float(f.read())

                counter = counter + 1

            #
            # Format data for db.
            #
            json_body[0]['fields'] = endpoints
            #log.info("json_body[fields]: %s" % json_body[0]['fields'])

            #
            # Insert data into db
            #
            # pprint.pprint(json_body)
            db_client.write_points(json_body)

            # Log (sparingly) for reassurance.
            if time.time() - now > log_status_period:
                log.info("stored %s records" % counter)
                now = time.time()

            # Wait for the next time ...
            time.sleep(api_fetch_period)

    except Exception as e:
        log.error("Caught Exception, Exiting")
        running = False

    finally:
        log.info("Closing db client connection")
        db_client.close()


if __name__ == "__main__":
    log.info("Started")
    signal.signal(signal.SIGTERM, handler)  # assign the handler to the signal SIGTERM
    main()
    log.info("Exited\n\n")
