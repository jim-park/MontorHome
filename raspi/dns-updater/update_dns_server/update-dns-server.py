#!/usr/bin/env python

__author__ = "James Park, Linux Networks Ltd"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"


import re
import os
import sys
import boto3
from redis import Redis, RedisError
from socket import timeout
import ConfigParser
from time import sleep

# Globals.
IP_ADDR_REGEX = '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'

# Set a dbhost (Mainly for development).
dbhost = os.getenv('DBHOST', 'redis')

# Get a DB connection pool and a subscriber.
redis = Redis(host=dbhost, db=0, socket_connect_timeout=2, socket_timeout=2)
sub = redis.pubsub(ignore_subscribe_messages=True)

# Initialise config from files.
try:
    # Read general config.
    config = ConfigParser.SafeConfigParser()
    config.read("/dns-updater-conf")
    # Read protected config (location is docker secrets).
    aws_credentials = ConfigParser.SafeConfigParser()
    aws_credentials.read("/run/secrets/aws-credentials")
except Exception as e:
    print "Failed to read config file. Cannot start. Exiting. %s" % e
    sys.exit(-1)

# Load config.
try:
    # NOTE: 'domain_name' is the url whos ip address we want to keep up to date.
    # It is also used as an identifier for;
    #   - redis channel name to subscribe to for IP address change events.
    domain_name = config.get("default", "domain_name")
    aws_hosted_zone_id = aws_credentials.get("aws", "aws_hosted_zone_id")
    aws_access_key_id = aws_credentials.get("aws", "aws_access_key_id")
    aws_secret_access_key = aws_credentials.get("aws", "aws_secret_access_key")
    db_conn_retry_peiod = float(config.get("default", 'db_conn_retry_period'))
    # Dump config.
    print "loaded config:\n" \
          "\t'aws_hosted_zone_id'    : '%s'\n" \
          "\t'aws_access_key_id'     : '%s'\n" \
          "\t'aws_secret_access_key' : '%s'\n" \
          "\t'domain_name'           : '%s'\n" \
          "\t'db_conn_retry_period'  : '%s'\n" \
          % (aws_hosted_zone_id, aws_access_key_id, aws_secret_access_key, domain_name, db_conn_retry_peiod)
except Exception as e:
    print "Failed to load all config items and/or AWS credentials. Cannot start. Exiting. %s" % e
    sys.exit(-1)


#
# Update the IP address for a domain on Route53.
# This function is called as a callback.
#
def update_aws_route53(message):

    ip_addr = message['data']

    # Don't continue without a valid ip address.
    m = re.match(IP_ADDR_REGEX, ip_addr)
    if not m:
        return False

    print "Updating Route53 DNS entry for '%s' to '%s'." % (domain_name, ip_addr)
    try:
        # Setup the client.
        client = boto3.client('route53',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key)

        # Update IP address for domain 'domain_name' on the Route 53 DNS server.
        resp = client.change_resource_record_sets(
            HostedZoneId=aws_hosted_zone_id,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': domain_name,
                            'Type': 'A',
                            'TTL': 300,
                            'ResourceRecords': [
                                {
                                    'Value': ip_addr
                                },
                            ],
                        }
                    },
                ]
            }
        )
    except Exception as e:
        print "Failed to update Route53 DNS. Update abandoned. %s" % e
        return False

    # Now track the status of the change requested via the returned change ID.
    change_status = resp['ChangeInfo']['Status']
    change_id = resp['ChangeInfo']['Id']
    print "Route53 DNS change request '%s' submitted." % change_id

    # Loop and keep checking if the change has been applied.
    while change_status not in ['INSYNC']:
        sleep(10)
        # Update the status of the change.
        resp = client.get_change(
            Id=change_id
        )
        change_status = resp['ChangeInfo']['Status']
        print "Change '%s' status: '%s'" % (change_id, change_status)
        # TODO: Don't rely on AWS not to leave us looping forever. Add a timeout in here.

    # Change has been applied and DNS records are 'INSYNC'.
    print "Route53 DNS update successful."

    # Update cache once change is complete.
    try:
        redis.set(domain_name, ip_addr)
        print "Cache item '%s' updated to '%s'" % (domain_name, ip_addr)
    except RedisError as e:
        print "Failed to update cache item '%s'. %s" % (domain_name, e)
        # Not a problem if it fails.
        # The next update check will retry (because we know the cached IP is now wrong).


def db_connect():

    success = False
    while not success:
        # Subscribe to channel and set callback.
        try:
            sub.subscribe(**{domain_name: update_aws_route53})
            success = True
            print "Connected. Polling for message from channel '%s'" % domain_name
        except RedisError as e:
            print "Failed to subscribe to update channel. %s" % e
            sleep(db_conn_retry_peiod)


#
# Main
#
def main():
    print "Running."

    db_connect()

    # Loop and poll.
    while True:
        try:
            sub.get_message(timeout=5.0)
        except timeout:
            pass
        except RedisError as e:
            print "Error. Subscription to '%s' lost, or db connection lost. %s" % (domain_name, e)
            db_connect()


if __name__ == "__main__":
    main()
