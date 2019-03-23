#!/usr/bin/env python

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

# Initialise redis connectionpool.
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
    success = False
    while not success == True:
        try:
            success = redis.ping()
            print "Connected to cache db"
        except RedisError as e:
            print "Failed to connect to cache db. %s" % e
            print "Will retry connection in %s secs." % db_conn_retry_period
            sleep(db_conn_retry_period)


# On startup (or DB reset). Initialise cache value to reflect resolved DNS value.
def init_cache():
    resolved_ip_addr = socket.gethostbyname(domain_name)
    try:
        redis.set(domain_name, resolved_ip_addr)
        print "setting cached ip: %s" % resolved_ip_addr
    except RedisError as e:
        connect_to_db()


#
# Main
#
def main():
    print "Running."
    global check_period


    # Setup period timer.
    now = datetime.now
    delta = timedelta(seconds=check_period)
    start = now() - delta     # To force an initial run, as opposed to an initial wait.

    while True:

        # Execute this block every 'delta' seconds.
        if start + delta < now():
            # Initialise variables.
            retry = False
            actual_ext_ip_addr = False
            cached_ip = False


            # Fetch our external ip address from containerised Flask app.
            try:
                actual_ext_ip_addr = urllib2.urlopen(request).read()
            except (URLError, socket.error) as e:
                print "Failed to get external IP address. Is 'fetch-ext-ip-addr' container running? Will retry."
                retry = True


            # Retreive our cached IP address from redis DB.
            try:
                cached_ip = redis.get(domain_name)
                # Initial run, or the db got reset ... for some reaseon.
                if not cached_ip:
                    init_cache()
                    cached_ip = redis.get(domain_name)
            except RedisError as e:
                print "Failed to get cached IP address. Will retry."
                retry = True


            if actual_ext_ip_addr and cached_ip:

                # If there's been a change of extrnal IP address, kick off a DNS server update.
                if actual_ext_ip_addr != cached_ip:
                    print "DNS update required."

                    print "Publishing '%s' on channel '%s'." % (actual_ext_ip_addr, domain_name)
                    try:
                        redis.publish(domain_name, actual_ext_ip_addr)
                    except RedisError as e:
                        print "Failed to publish '%s' on channel '%s'. Will retry. %s" % (actual_ext_ip_addr, domain_name, e)
                        retry = True

                # External IP address remains the same. No action.
                else:
                    print "DNS records up to date (%s). No update required." % actual_ext_ip_addr


            # Reset timmer if we don't need to retry.
            if not retry:
                start = now()
                # Re-read config, Update delta period.
                config.read('/dns-updater-conf')
                check_period = config.getint("main", 'check_period')
                delta = timedelta(seconds=check_period)


        # Take it easy around this loop.
        # This delay limits the retry rate.
        sleep(5.0)


if __name__ == "__main__":
    main()
