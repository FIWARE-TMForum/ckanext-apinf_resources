# -*- coding: utf-8 -*-

# Copyright (c) 2017 CoNWeT Lab., Universidad Politécnica de Madrid
#
# This file belongs to the Apinf resources CKAN extension
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import requests
from urlparse import urlparse

import ckan.plugins.toolkit as toolkit

from ckanext.apinf_resources.errors import AuthenticationError


PAGE_LEN = 100


def authenticated_request(func):
    def wrapper(*args, **kwargs):

        # Check if the instance is authenticated in Apinf
        self = args[0]
        if self._user_id is None or self._user_token is None:
            raise AuthenticationError(toolkit._('There has been an error authenticating CKAN with configured Apinf instance'))

        return func(*args, **kwargs)

    return wrapper


class ApinfClient:

    def __init__(self):
        # Get configuration params
        self._umbrella_url = toolkit.config.get('ckan.apinf_resources.umbrella_url', '')
        self._umbrella_key = toolkit.config.get('ckan.apinf_resources.umbrella_key', '')
        self._umbrella_token = toolkit.config.get('ckan.apinf_resources.umbrella_token', '')

        self._apinf_url = toolkit.config.get('ckan.apinf_resources.apinf_url', '')
        self._parsed_apinf = urlparse(self._apinf_url)

        self._user_id = None
        self._user_token = None

        self._login()

    def _login(self):
        apinf_admin = toolkit.config.get('ckan.apinf_resources.admin_name', '')
        apinf_pwd = toolkit.config.get('ckan.apinf_resources.admin_pass', '')

        body = {
            'username': apinf_admin,
            'password': apinf_pwd
        }

        url = '{}://{}/rest/v1/login'.format(self._parsed_apinf.scheme, self._parsed_apinf.netloc)
        resp = requests.post(url, json=body)

        if resp.status_code == 200:
            auth_data = resp.json()

            # Save userId and authToken info required by secured Apinf APIs
            self._user_id = auth_data['data']['userId']
            self._user_token = auth_data['data']['authToken']

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

                start += PAGE_LEN
            else:
                processed = True

        return target_url

    def _get_backend_api(self, api_url):
        # Check if an API Umbrella instance has been configured
        if not len(self._umbrella_url):
            return

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

        return self._process_apis(url, '&start={}&length=' + unicode(PAGE_LEN), matcher, headers={
            'X-Api-Key': self._umbrella_key,
            'X-Admin-Auth-Token': self._umbrella_token
        })

    def get_apinf_page(self, api_url):
        """
        Generates the URL of the Apinf page which contains the service level description of the API which is serving
        a given dataset resource
        :param api_url: URL of the dataset resource
        :return: Apinf page or None
        """
        # This step is needed for prev Apinf versions which do not include the proxied URL as 'url' param
        backend_api = self._get_backend_api(api_url)
        backend_path = []

        if backend_api is None:
            # The API is not included is API Umbrella or Umbrella has not been queried (new Apinf version)
            parsed_api = urlparse(api_url)
            backend_api = '{}://{}'.format(parsed_api.scheme, parsed_api.netloc)
            backend_path = [path for path in parsed_api.path.split('/') if path != '']

        # Get Apinf APIs
        def matcher(api):
            target_api = None

            if api['url'].startswith(backend_api):
                # Check if API include paths
                parsed_target = urlparse(api['url'])
                front_path = [path for path in parsed_target.path.split('/') if path != '']

                if len(front_path) <= len(backend_path) and front_path == backend_path[:len(front_path)]:
                    target_api = '{}://{}/apis/{}'.format(self._parsed_apinf.scheme, self._parsed_apinf.netloc, api['slug'])

            return target_api

        url = '{}://{}/rest/v1/apis'.format(self._parsed_apinf.scheme, self._parsed_apinf.netloc)

        return self._process_apis(url, '?skip={}&limit=' + unicode(PAGE_LEN), matcher)

    def _make_organization_request(self, ep_url, method, name, description, url, contact_name, contact_email, contact_phone):
        org_body = {
            'name': name,
            'description': description,
            'url': url,
            'contact_name': contact_name,
            'contact_email': contact_email,
            'contact_phone': contact_phone
        }

        return method(ep_url, json=org_body, headers={
            'X-User-Id': self._user_id,
            'X-Auth-Token': self._user_token
        })

    @authenticated_request
    def create_organization(self, name, description, url, contact_name, contact_email, contact_phone):
        """
        Create a new organization in Apinf
        :param name: Name of the new organization
        :param description: Description of the organization
        :param url: URL of the organization or web site
        :param contact_name: Name of the organization contact
        :param contact_email: Email of the organization contact
        :param contact_phone: Phone of the organization contact
        :return: the Id of the new organization created in Apinf
        """
        org_id = None
        ep_url = '{}://{}/rest/v1/organizations'.format(self._parsed_apinf.scheme, self._parsed_apinf.netloc)

        resp = self._make_organization_request(
            ep_url, requests.post, name, description, url, contact_name, contact_email, contact_phone)

        if resp.status_code == 201:
            org_data = resp.json()
            org_id = org_data['data']['_id']

        return org_id

    @authenticated_request
    def update_organization(self, org_id, name, description, url, contact_name, contact_email, contact_phone):
        """
        Update an organization in Apinf
        :param name: Name of the new organization
        :param description: Description of the organization
        :param url: URL of the organization or web site
        :param contact_name: Name of the organization contact
        :param contact_email: Email of the organization contact
        :param contact_phone: Phone of the organization contact
        :return: the Id of the new organization created in Apinf
        """
        ep_url = '{}://{}/rest/v1/organizations/{}'.format(self._parsed_apinf.scheme, self._parsed_apinf.netloc, org_id)
        self._make_organization_request(
            ep_url, requests.put, name, description, url, contact_name, contact_email, contact_phone)

    @authenticated_request
    def delete_organization(self, org_id):
        pass
