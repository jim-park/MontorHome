#!/usr/bin/env python

import os
import time
import signal
import urllib
import pprint
from influxdb import InfluxDBClient

# Get and assign os environment vars.
log_status_period = float(os.getenv('LOG_STATUS_PERIOD', 1800))
api_url = os.getenv('API_URL')
api_http_port = os.getenv('API_HTTP_PORT')
api_fetch_period = float(os.getenv('API_FETCH_PERIOD'))
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
endpoints_env = [i for i in os.environ.get("ENDPOINTS").split(" ")]

# Make endpoints dict from endpoints env var.
endpoints = dict()
for ep in endpoints_env:
    endpoints[ep] = None

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


# Main run loop
def main():
    global running

    json_body = [{
        "measurement": "fast_data",
        "fields": {}
    }]

    # For logging only.
    now = time.time() - log_status_period
    counter = 0

    try:
        db_connect()
        while running:

            #
            # Fetch data from all endpoints.
            #
            for endpoint in endpoints.keys():
                #db_client.delete_series(db_name, endpoint)

                url = "%s:%s/%s" % (api_url, api_http_port, endpoint)
                f = urllib.urlopen(url)
                endpoints[endpoint] = float(f.read())

                counter = counter + 1

            #
            # Format data for db.
            #
            json_body[0]['fields'] = endpoints
            # print "json_body[fields]: %s" % json_body[0]['fields']

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
