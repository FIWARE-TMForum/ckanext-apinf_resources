from __future__ import unicode_literals


import unittest
from mock import MagicMock, call
from parameterized import parameterized


from ckanext.apinf_resources.apinf import apinf_client


class ApinfClientTestCase(unittest.TestCase):

    _umbrella_api1 = {
        "backend_host": "context.url.eu:1026",
        "backend_protocol": "http",
        "frontend_host": "umbrella.url:8443",
        "name": "Test Broker",
        "servers": [
            {
                "host": "context.url.eu",
                "port": 1026,
                "id": "530d770a-7441-45ab-bb11-8ca0e20ae94a"
            }
        ],
        "url_matches": [
            {
                "backend_prefix": "/",
                "frontend_prefix": "/broker/",
                "id": "a93471e6-0ee9-470a-b69b-bfb4c1dc484c"
            }
        ],
        "version": 2,
        "id": "2f9f467e-0911-4dc1-92c2-abd44846a95a",
        "frontend_prefixes": "/broker/"
    }

    _umbrella_api2 = {
        "backend_host": "example.service.com",
        "backend_protocol": "http",
        "frontend_host": "umbrella.url:8443",
        "name": "Test Service",
        "servers": [
            {
                "host": "example.service.com",
                "port": 80,
                "id": "530d770a-7441-45ab-bb11-8ca0e20ae94a"
            }
        ],
        "url_matches": [
            {
                "backend_prefix": "/",
                "frontend_prefix": "/api/",
                "id": "a93471e6-0ee9-470a-b69b-bfb4c1dc484c"
            }
        ],
        "version": 2,
        "id": "2f9f467e-0911-4dc1-92c2-abd44846a95a",
        "frontend_prefixes": "/api/"
    }

    _umbrella_api3 = {
        "backend_host": "context.fiware.com",
        "backend_protocol": "https",
        "frontend_host": "umbrella.url:8443",
        "name": "Other Broker",
        "servers": [
            {
                "host": "context.fiware.com",
                "port": 443,
                "id": "530d770a-7441-45ab-bb11-8ca0e20ae94a"
            }
        ],
        "url_matches": [
            {
                "backend_prefix": "/",
                "frontend_prefix": "/fiware/service/",
                "id": "a93471e6-0ee9-470a-b69b-bfb4c1dc484c"
            }
        ],
        "version": 2,
        "id": "2f9f467e-0911-4dc1-92c2-abd44846a95a",
        "frontend_prefixes": "/fiware/service/"
    }

    _umbrella_api4 = {
        "backend_host": "service.opplafy.com:1027",
        "backend_protocol": "http",
        "frontend_host": "umbrella.url:8443",
        "name": "Other Broker",
        "servers": [
            {
                "host": "service.opplafy.com",
                "port": 1027,
                "id": "530d770a-7441-45ab-bb11-8ca0e20ae94a"
            }
        ],
        "url_matches": [
            {
                "backend_prefix": "/",
                "frontend_prefix": "/service/",
                "id": "a93471e6-0ee9-470a-b69b-bfb4c1dc484c"
            }
        ],
        "version": 2,
        "id": "2f9f467e-0911-4dc1-92c2-abd44846a95a",
        "frontend_prefixes": "/service/"
    }

    _apinf_api1 = {
        "name": "Local Context Broker",
        "url": "http://orion.docker:1026/",
        "lifecycleStatus": "development",
        "managerIds": [
            "aqEnwJeGGX6ZaDrXk"
        ],
        "slug": "local-broker"
    }

    _apinf_api2 = {
        "name": "FIWARE Context Broker",
        "url": "https://context.fiware.com/",
        "lifecycleStatus": "development",
        "managerIds": [
            "aqEnwJeGGX6ZaDrXk"
        ],
        "slug": "fiware-broker"
    }

    _apinf_api3 = {
        "name": "Opp Service",
        "url": "http://service.opplafy.com:1027/",
        "lifecycleStatus": "development",
        "managerIds": [
            "aqEnwJeGGX6ZaDrXk"
        ],
        "slug": "broker-1"
    }

    _umbrella_host = 'http://umbrella.url:8443'
    _apinf_host = 'https://apinf.url/'

    _key = 'umbrellakey'
    _token = 'admintoken'

    _umbrella_headers = {
        'X-Api-Key': _key,
        'X-Admin-Auth-Token': _token
    }

    def setUp(self):
        # Mock CKAN config
        apinf_client.config = {
            'ckan.apinf_resources.umbrella_url': self._umbrella_host,
            'ckan.apinf_resources.umbrella_key': self._key,
            'ckan.apinf_resources.umbrella_token': self._token,
            'ckan.apinf_resources.apinf_url': self._apinf_host
        }

        apinf_client.PAGE_LEN = 2
        apinf_client.requests = MagicMock()

    def _build_response(self, body, status=200):
        response = MagicMock(status_code=status)
        response.json.return_value = {'data': body}
        return response

    def _mock_requests_results(self):

        response1 = self._build_response([self._umbrella_api1, self._umbrella_api2])
        response2 = self._build_response([self._umbrella_api3, self._umbrella_api4])
        response3 = self._build_response([self._apinf_api1, self._apinf_api2])
        response4 = self._build_response([self._apinf_api3])

        apinf_client.requests.get.side_effect = [response1, response2, response3, response4]

    def _mock_multiple_path_requests(self):
        response1 = self._build_response([self._umbrella_api1, self._umbrella_api2])
        response2 = self._build_response([self._umbrella_api3, self._umbrella_api4])
        response3 = self._build_response([self._apinf_api1, self._apinf_api2])
        apinf_client.requests.get.side_effect = [response1, response2, response3]

    def _mock_non_proxied_requests(self):
        response = self._build_response([self._apinf_api1, self._apinf_api2])
        apinf_client.requests.get.side_effect = [response]

    def _mock_missing_paths_requests(self):
        response1 = self._build_response([self._apinf_api1, self._apinf_api2])
        response2 = self._build_response([self._apinf_api3])
        response3 = self._build_response([])
        apinf_client.requests.get.side_effect = [response1, response2, response3]

    def _mock_error_requests(self):
        response1 = self._build_response([], status=500)
        response2 = self._build_response([])
        apinf_client.requests.get.side_effect = [response1, response2]

    def _mock_not_found_requests(self):
        response1 = self._build_response([self._umbrella_api1, self._umbrella_api2])
        response2 = self._build_response([])
        response3 = self._build_response([])
        apinf_client.requests.get.side_effect = [response1, response2, response3]

    def _check_requests_calls(self):
        self.assertEquals([
            call(self._umbrella_host + '/api-umbrella/v1/apis?search[value]=service&start=0&length=2', headers=self._umbrella_headers, verify=False),
            call(self._umbrella_host + '/api-umbrella/v1/apis?search[value]=service&start=2&length=2', headers=self._umbrella_headers, verify=False),
            call(self._apinf_host + 'rest/v1/apis?skip=0&limit=2', headers={}, verify=False),
            call(self._apinf_host + 'rest/v1/apis?skip=2&limit=2', headers={}, verify=False)
        ], apinf_client.requests.get.call_args_list)

    def _check_multiple_path_requests(self):
        self.assertEquals([
            call(self._umbrella_host + '/api-umbrella/v1/apis?search[value]=fiware&start=0&length=2', headers=self._umbrella_headers, verify=False),
            call(self._umbrella_host + '/api-umbrella/v1/apis?search[value]=fiware&start=2&length=2', headers=self._umbrella_headers, verify=False),
            call(self._apinf_host + 'rest/v1/apis?skip=0&limit=2', headers={}, verify=False)
        ], apinf_client.requests.get.call_args_list)

    def _check_non_proxied_requests(self):
        self.assertEquals([
            call(self._apinf_host + 'rest/v1/apis?skip=0&limit=2', headers={}, verify=False)
        ], apinf_client.requests.get.call_args_list)

    def _check_missing_paths_requests(self):
        self.assertEquals([
            call(self._apinf_host + 'rest/v1/apis?skip=0&limit=2', headers={}, verify=False),
            call(self._apinf_host + 'rest/v1/apis?skip=2&limit=2', headers={}, verify=False),
            call(self._apinf_host + 'rest/v1/apis?skip=4&limit=2', headers={}, verify=False)
        ], apinf_client.requests.get.call_args_list)

    def _check_umbrella_error_requests(self):
        self.assertEquals([
            call(self._umbrella_host + '/api-umbrella/v1/apis?search[value]=service&start=0&length=2', headers=self._umbrella_headers, verify=False),
            call(self._apinf_host + 'rest/v1/apis?skip=0&limit=2', headers={}, verify=False)
        ], apinf_client.requests.get.call_args_list)

    def _check_not_found_requests(self):
        self.assertEquals([
            call(self._umbrella_host + '/api-umbrella/v1/apis?search[value]=service&start=0&length=2', headers=self._umbrella_headers, verify=False),
            call(self._umbrella_host + '/api-umbrella/v1/apis?search[value]=service&start=2&length=2', headers=self._umbrella_headers, verify=False),
            call(self._apinf_host + 'rest/v1/apis?skip=0&limit=2', headers={}, verify=False)
        ], apinf_client.requests.get.call_args_list)

    @parameterized.expand([
        ('published', 'http://umbrella.url:8443/service/v2/entities?type=Parking',
         'https://apinf.url/apis/broker-1', _mock_requests_results, _check_requests_calls),
        ('multiple_path', 'http://umbrella.url:8443/fiware/service/v2/entities?type=Parking',
         'https://apinf.url/apis/fiware-broker', _mock_multiple_path_requests, _check_multiple_path_requests),
        ('non_proxied', 'http://orion.docker:1026/v2/entities?type=Air', 'https://apinf.url/apis/local-broker',
         _mock_non_proxied_requests, _check_non_proxied_requests),
        ('missing_paths', 'http://umbrella.url:8443/', None, _mock_missing_paths_requests, _check_missing_paths_requests),
        ('error_umbrella', 'http://umbrella.url:8443/service/v2/entities?type=Parking', None,
         _mock_error_requests, _check_umbrella_error_requests),
        ('not_found_umbrella', 'http://umbrella.url:8443/service/v2/entities?type=Parking', None,
         _mock_not_found_requests, _check_not_found_requests)
    ])
    def test_get_apinf_page(self, name, url, exp_url, requests_mocker, request_checker):
        # Mock requests
        requests_mocker(self)

        # Call apinf client
        client = apinf_client.ApinfClient()
        apinf_url = client.get_apinf_page(url)

        # Check response and calls
        self.assertEquals(exp_url, apinf_url)
        request_checker(self)
