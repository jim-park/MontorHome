#!/usr/bin/env python

__author__ = "James Park, Linux Networks Ltd"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"


import os
import urllib2
from urllib2 import URLError
import socket
import ConfigParser
from redis import Redis, RedisError
from datetime import datetime, timedelta
from time import sleep


# Initialise config.
config = ConfigParser.SafeConfigParser()
config.read("/dns-updater-conf")

# Set var for communicating with other containers. Mainly for development purposes.
dbhost = os.getenv('DBHOST', 'redis')
fetch_ext_ip_api_url = os.getenv('FETCHEXTIPHOSTURL', 'http://fetch-ext-ip-addr/do')

# Initialise redis connection pool.
redis = Redis(host=dbhost, db=0, socket_connect_timeout=2, socket_timeout=2)

# Load config
# NOTE: 'domain_name' is the url whos ip address we want to keep up to date.
# It is also used as an identifier for;
#   - redis channel name to publish an update event.
#   - redis item key to store the external IP address against.
domain_name = config.get("default", 'domain_name')
db_conn_retry_period = config.getfloat("default", 'db_conn_retry_period')
check_period = config.getint("main", 'check_period')
print "loaded config:\n" \
      "\t'domain_name'          : '%s'\n" \
      "\t'check_period'         : '%s'\n" \
      "\t'db_conn_retry_period' : '%s'\n" \
      % (domain_name, check_period, db_conn_retry_period)

# Initialise urlreqest for fetch-ext-ip-addr.
request = urllib2.Request(fetch_ext_ip_api_url)


# Waits for cache db to become active.
def connect_to_db():
    retries = 3

    while retries > 0:
        try:
            redis.ping()
        except RedisError as e:
            print "Couldn't connect to cache db. {0}".format(e)
            retries = retries - 1
            if retries > 0:
                print "Will retry db connection in {0} secs.".format(db_conn_retry_period)
                sleep(db_conn_retry_period)
        else:
            print "Connected to cache db"
            break

    if retries <= 0:
        raise Exception("Failed to connect to cache db.")


def init_cache():
    """ On startup or DB reset. Initialise cache value to reflect resolved DNS value. """

    try:
        resolved_ip_addr = socket.gethostbyname(domain_name)
    except socket.error as e:
        raise Exception("Failed to resolve domain name. e: {0}".format(e))

    try:
        connect_to_db()
    except Exception as e:
        raise e

    try:
        redis.set(domain_name, resolved_ip_addr)
    except RedisError as e:
        raise e
    else:
        print "cached IP address set to: {0}".format(resolved_ip_addr)

    return resolved_ip_addr


#
# Main
#
def main():
    global check_period

    # Setup period timer.
    now = datetime.now
    delta = timedelta(seconds=check_period)
    start = now() - delta     # To force an initial run, as opposed to an initial wait.

    while True:

        # Execute this block every 'delta' seconds.
        if start + delta < now():
            # Initialise variables.
            actual_ext_ip_addr = False
            cached_ip = False

            try:

                # Fetch our external ip address from containerised Flask app.
                try:
                    response = urllib2.urlopen(request)
                except (socket.error, URLError) as e:
                    raise Exception("Failed to get external IP address from container url '{1}'. e: {0}".format(e, fetch_ext_ip_api_url))
                else:
                    actual_ext_ip_addr = response.read()

                # Retrieve our cached IP address from redis DB.
                try:
                    cached_ip = redis.get(domain_name)
                except RedisError:
                    try:
                        cached_ip = init_cache()
                    except Exception as e:
                        raise Exception("Failed to get cached IP address. e: {0}".format(e))

                if actual_ext_ip_addr != cached_ip:
                    print "DNS update required."
                    print "Publishing '{0}' on channel '{1}'.".format(actual_ext_ip_addr, domain_name)

                    try:
                        redis.publish(domain_name, actual_ext_ip_addr)
                    except RedisError as e:
                        raise Exception("Failed to publish '{0}' on channel '{1}'. e: {2}".format(actual_ext_ip_addr, domain_name, e))

                # External IP address remains the same. No action.
                else:
                    print "DNS records up to date ({0}). No update required.".format(cached_ip)

            except Exception as e:
                # We failed to get either the actual external or cached IP address.
                # An exception (above) should contain the error.
                print "Failed to determine if DNS update is required."
                print "reason - {0}".format(e)
                print "  External IP address:        {0}".format(actual_ext_ip_addr)
                print "  Cached external IP address: {0}".format(cached_ip)

            finally:
                # Reset timer, re-read config and update delta period.
                start = now()
                config.read('/dns-updater-conf')
                delta = timedelta(seconds=config.getint("main", 'check_period'))

        # Take it easy around this loop.
        sleep(5.0)


if __name__ == "__main__":
    main()
