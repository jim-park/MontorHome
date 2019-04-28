#!/usr/bin/env python

__author__ = "James Park, Linux Networks Ltd"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"


import urllib2
import time
import re
import ConfigParser
from flask import Flask, abort
from pprint import pprint

# Constants.
IP_ADDR_REGEX = '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
HTTP_HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
            AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}


def create_app(test_config=None):

    app = Flask(__name__)

    #
    # Initialise config.
    #
    if test_config is None:
        config = ConfigParser.SafeConfigParser()
        config.read("/dns-updater-conf")
        # Assign config values read from file to app config object.
        app.config['ip_addr_fetch_url'] = config.get('fetch-ext-ip-addr', 'ip_addr_fetch_url')
        app.config['fetch_retries'] = config.get('fetch-ext-ip-addr', 'fetch_retries')
    else:
        app.config.update(test_config)
        print "TEST MODE ON."

    # Dump config to log.
    print "Loaded config:"
    pprint({item: app.config[item] for item in app.config}, indent=2)

    #
    # Function to fetch the external IP address (as seen by the internet).
    #
    @app.route("/do")
    def do_fetch():

        # Dump current config to log for testing or debug.
        if app.config['TESTING'] or app.config['DEBUG']:
            print "Using config:"
            pprint({item: app.config[item] for item in app.config}, indent=2)

        # Instantiate http url request object.
        ip_addr_fetch_url = app.config['ip_addr_fetch_url']
        request = urllib2.Request(ip_addr_fetch_url, headers=HTTP_HEADERS)

        # Setup retry counter.
        retry = int(app.config['fetch_retries'])

        while retry > 0:

            try:
                # Fetch our ip address from url, read it and strip it.
                response = urllib2.urlopen(request)

                # print "resp: %s" % response
                # print "resp.__dict__: %s" % response.__dict__

                # Check response status is ok.
                if response.getcode() != 200:
                    raise(Exception("Response was not 200 ok, got {0}.".format(response.getcode())))

                # Read and tidy up the response data.
                ip_addr_str = response.read().strip()

                # Check the response data looks like an IP address.
                if not re.match(IP_ADDR_REGEX, ip_addr_str):
                    raise (Exception("Response was not an IP address."))

                # All checks passed, it's good to return.
                print "Fetched external IP address ok - {0}".format(ip_addr_str)
                return ip_addr_str

            except (urllib2.URLError, Exception) as e:
                print "Exception getting external IP address from: {0}. Error: {1}".format(ip_addr_fetch_url, e)
                # A retry is required. Decrement counter and wait a moment.
                retry = retry - 1
                time.sleep(0.5)

        # If we've reached here, our external IP address was not found,
        # 404 is the appropriate response.
        print "Given up, returning 404."
        abort(404)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=80)
