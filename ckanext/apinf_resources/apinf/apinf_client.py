from __future__ import unicode_literals

import requests
from urlparse import urlparse

from ckan.common import config


class ApinfClient:

    def __init__(self):
        # Get configuration params
        self._umbrella_url = config.get('ckan.apinf_resources.umbrella_url', '')
        self._umbrella_key = config.get('ckan.apinf_resources.umbrella_key', '')
        self._umbrella_token = config.get('ckan.apinf_resources.umbrella_token', '')

        self._apinf_url = config.get('ckan.apinf_resources.apinf_url', '')

    def _process_apis(self, base_url, pag_tmpl, matcher, headers={}):
        target_url = None

        processed = False
        start = 0
        while not processed:
            url = base_url + pag_tmpl.format(start)

            response = requests.get(url, headers=headers, verify=False)

            if response.status_code == 200:
                resp = response.json()

                # Validate frontend path
                if not len(resp['data']):
                    processed = True

                for api in resp['data']:
                    target_url = matcher(api)

                    if target_url is not None:
                        processed = True
                        break

                start += 100
            else:
                processed = True

        return target_url

    def _get_backend_api(self, api_url):
        parsed_api = urlparse(api_url)
        parsed_umbrella = urlparse(self._umbrella_url)

        # Check that the provided URL is secured with the configured umbrella instance
        if parsed_api.netloc != parsed_umbrella.netloc or parsed_api.scheme != parsed_umbrella.scheme:
            return

        # Search in API umbrella using the URL path as query
        paths = [path for path in parsed_api.path.split('/') if path != '']

        if not len(paths):
            # The provided URL does not include a path, so it cannot be registered in API Umbrella
            return

        url = '{}://{}/api-umbrella/v1/apis?search[value]={}'.format(parsed_umbrella.scheme, parsed_umbrella.netloc, paths[0])

        def matcher(api):
            target_api = None
            front_path = [path for path in api['frontend_prefixes'].split('/') if path != '']

            if len(front_path) <= len(paths) and front_path == paths[:len(front_path)]:
                target_api = '{}://{}'.format(api['backend_protocol'], api['backend_host'])

            return target_api

        return self._process_apis(url, '&start={}&length=100', matcher, headers={
            'X-Api-Key': self._umbrella_key,
            'X-Admin-Auth-Token': self._umbrella_token
        })

    def get_apinf_page(self, api_url):
        parsed_apinf = urlparse(self._apinf_url)
        backend_api = self._get_backend_api(api_url)

        if backend_api is None:
            # The API is not included is API Umbrella, so it may has not been proxied
            parsed_api = urlparse(api_url)
            backend_api = '{}://{}'.format(parsed_api.scheme, parsed_api.netloc)

        # Get Apinf APIs
        def matcher(api):
            target_api = None
            if api['url'].startswith(backend_api):
                # Build Apinf page
                target_api = '{}://{}/apis/{}'.format(parsed_apinf.scheme, parsed_apinf.netloc, api['slug'])

            return target_api

        url = '{}://{}/rest/v1/apis'.format(parsed_apinf.scheme, parsed_apinf.netloc)

        return self._process_apis(url, '?skip={}&limit=100', matcher)
