#!/usr/bin/env python

import urllib2
import time
import re
import ConfigParser
from flask import Flask

# Globals.
IP_ADDR_REGEX = '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
HTTP_HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
            AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}

# Initialise config.
config = ConfigParser.SafeConfigParser()
config.read("/dns-updater-conf")

# Load and dump out config.
ip_addr_fetch_url = config.get("fetch-ext-ip-addr", 'ip_addr_fetch_url', 'http://ifconfig.co/ip')
fetch_retries = int(config.get("fetch-ext-ip-addr", 'fetch_retries', 3))
print "loaded config:\n" \
      "\t'ip_addr_fetch_url' : '%s'\n" \
      "\t'fetch_retries'     : '%s'\n" \
      % (ip_addr_fetch_url, fetch_retries)

# Initialise http url request.
request = urllib2.Request(ip_addr_fetch_url, headers=HTTP_HEADERS)

# Start Flask.
app = Flask(__name__)


#
# Fetch the external IP address (as seen by the internet).
#
@app.route("/do")
def main():
        retry = fetch_retries

        while retry > 0:

            try:
                # Fetch our ip address from url, read it and strip it.
                ip_addr_str = urllib2.urlopen(request).read().strip()

                # Check the response looks like an IP address.
                m = re.match(IP_ADDR_REGEX, ip_addr_str)
                if not m:
                    raise (Exception("Response was not an IP address."))
                print "Fetched external IP address ok - {0}".format(ip_addr_str)

                return ip_addr_str

            except (urllib2.URLError, Exception) as e:
                print "Failed to retrieve external IP address from: {0}. Error: {1}".format(ip_addr_fetch_url, e)

                # A retry is required. Decrement counter and wait a moment.
                retry = retry - 1
                time.sleep(0.5)

        return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
