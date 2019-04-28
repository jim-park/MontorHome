#!/usr/bin/env python

import unittest
from mock import Mock, patch
import StringIO

# Add the file under test to the path.
from fetch_ext_ip_addr import create_app

# Allow global access to app object.
app = None


class TestFetchExtIPAddr(unittest.TestCase):

    def setUp(self):
        """ Create test client with basic testing config set. """
        global app
        test_config = {'TESTING': True,
                       'DEBUG': True,
                       'ip_addr_fetch_url': 'http://ifconfig.co/ip',
                       'fetch_retries': '3'}

        app = create_app(test_config=test_config)
        self.client = app.test_client()

    @patch('fetch_ext_ip_addr.urllib2.urlopen')
    def test_fetch_ext_ip_addr_success(self, mock_urlopen):
        """ Test external IP address can be fetched successfully. """
        mocked_ip_addr = '10.1.1.9'

        # Mock a successful response.
        mock_resp = Mock()
        mock_resp.read.return_value = mocked_ip_addr
        mock_resp.getcode.return_value = 200
        mock_urlopen.return_value = mock_resp

        # Execute the app under test using our test_client to hit it.
        ip_under_test = self.client.get('/do').data

        # Assert the result.
        self.assertEqual(mocked_ip_addr, ip_under_test)

    @patch('fetch_ext_ip_addr.urllib2.urlopen')
    def test_fetch_ext_ip_addr_failure_404(self, mock_urlopen):
        """ Test external ip address checker website returning 404 """

        # Mock a 404 Not Found response.
        mock_resp = Mock()
        mock_resp.getcode.return_value = 404
        mock_urlopen.return_value = mock_resp

        # Execute the app under test using our test_client to hit it.
        status_code = self.client.get('/do').status_code

        # NOTE: status_code is an int.
        self.assertEqual(status_code, 404)

    @patch('fetch_ext_ip_addr.urllib2.urlopen')
    def test_fetch_ext_ip_addr_failure_bad_ip_address_returned(self, mock_urlopen):
        """ Test external ip address checker website returning something other than a valid IP address """

        # Mock a 200 ok with bad return data.
        mock_resp = Mock()
        mock_resp.getcode.return_value = 200
        mock_resp.read.return_value = 'this string is NOT AN IP ADDRESS'
        mock_urlopen.return_value = mock_resp

        # Execute the app under test using our test_client to hit it.
        status_code = self.client.get('/do').status_code

        # NOTE: status_code is an int.
        self.assertEqual(status_code, 404)


if __name__ == '__main__':
    unittest.main()
