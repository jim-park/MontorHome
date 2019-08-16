#!/usr/bin/env python

__author__ = "James Park, Linux Networks Ltd"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"


import urllib2
import ConfigParser
from datetime import datetime, timedelta
from time import sleep
import boto3
import signal
import re

# Constants.
IP_ADDR_REGEX = '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
HTTP_HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
            AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
CONFIG_FILE_PATH = '/etc/mh-dns-updater.conf'

# Initialise config.
config = ConfigParser.SafeConfigParser()
config.read(CONFIG_FILE_PATH)

# Load config
domain_name = config.get("default", 'domain_name')
check_period = config.getint("default", 'check_period')
aws_hosted_zone_id = config.get("default", "aws_hosted_zone_id")
ip_addr_fetch_url = config.get("default", "ip_addr_fetch_url")
print "loaded config:\n" \
      "\t'domain_name'          : '%s'\n" \
      "\t'check_period'         : '%s'\n" \
      "\t'ip_addr_fetch_url'    : '%s'\n" \
      "\t'aws_hosted_zone_id'    : '%s'\n" \
      % (domain_name, check_period, ip_addr_fetch_url, aws_hosted_zone_id)

# Instantiate http url request object.
request = urllib2.Request(ip_addr_fetch_url, headers=HTTP_HEADERS)

# Instantiate the AWS client object.
client = boto3.client('route53')


#
# Functions
#

#
# Fetch route53 IP address
#
def fetch_route53_ip_address(domain_name):

    domain_ip_addr = False

    print("Fetching Route53 DNS entry for '%s'" % domain_name)
    try:
        # Update IP address for domain 'domain_name' on the Route 53 DNS server.
        resp = client.list_resource_record_sets(
            HostedZoneId=aws_hosted_zone_id,
        )
    except Exception as e:
        print("Failed to fetch DNS entry from Route53. %s" % e)
        raise

    for entry in resp['ResourceRecordSets']:
        name = entry['Name']
        name = name[:-1]  # strip off trailing period '.'
        if domain_name == name:
            domain_ip_addr = entry['ResourceRecords'][0]['Value']
            print("%s %s" % (entry['Name'], domain_ip_addr))

    return domain_ip_addr


#
# Fetch external IP address
#
def fetch_external_ip__address():
    # Fetch our ip address from url, read it and strip it.
    response = urllib2.urlopen(request)

    # print "resp: %s" % response
    # print "resp.__dict__: %s" % response.__dict__

    # Check response status is ok.
    if response.getcode() != 200:
        raise (Exception("Response was not 200 ok, got {0}.".format(response.getcode())))

    # Read and tidy up the response data.
    ip_addr_str = response.read().strip()

    # Check the response data looks like an IP address.
    if not re.match(IP_ADDR_REGEX, ip_addr_str):
        raise (Exception("Response was not an IP address."))

    # All checks passed, it's good to return.
    print "Fetched external IP address ok - {0}".format(ip_addr_str)
    return ip_addr_str


#
# Update the IP address for a domain on Route53.
#
def update_aws_route53(ip_addr):

    # Don't continue without a valid ip address.
    m = re.match(IP_ADDR_REGEX, ip_addr)
    if not m:
        return False

    print "Updating Route53 DNS entry for '%s' to '%s'." % (domain_name, ip_addr)
    try:
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

    return True


#
# Main
#
def main():
    global check_period

    # Initialise variables.
    actual_ext_ip_addr = False
    cached_ip = False

    # Setup period timer.
    now = datetime.now
    delta = timedelta(seconds=check_period)
    start = now() - delta     # To force an initial run, as opposed to an initial wait.

    while running:

        # Execute this block every 'delta' seconds.
        if start + delta < now():
            try:

                # Fetch our external ip address.
                actual_ext_ip_addr = fetch_external_ip__address()

                # Set our cached IP address if it's not defined. (initial run).
                if not cached_ip:
                    cached_ip = fetch_route53_ip_address(domain_name)

                # Compare actual to cache.
                if actual_ext_ip_addr != cached_ip:
                    print "DNS update required."
                    if update_aws_route53(actual_ext_ip_addr):
                        cached_ip = actual_ext_ip_addr

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
                config.read(CONFIG_FILE_PATH)
                delta = timedelta(seconds=config.getint("default", 'check_period'))

        # Take it easy around this loop.
        sleep(5.0)


# Global flag for loop exit
running = True


#
# Signal handler for graceful exit.
#
def receive_signal(signal_number, frame):
    global running
    if signal_number == signal.SIGINT:
        print('Received SIGINT. Exiting')
        running = False
    else:
        print("Received signal: %s, ignoring" % signal_number)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, receive_signal)
    main()
