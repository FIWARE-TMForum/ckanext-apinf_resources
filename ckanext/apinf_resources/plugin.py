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

from urlparse import urlparse

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from apinf.apinf_client import ApinfClient
from errors import AuthenticationError


class Apinf_ResourcesPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IOrganizationController, inherit=True)

    def __init__(self, name=None):
        self._client = ApinfClient()

    # IOrganizationController
    def create(self, entity):
        ckan_url = urlparse(toolkit.config.get('ckan.site_url'))
        url = '{}://{}/organization/{}'.format(ckan_url.scheme, ckan_url.netloc, entity.name)

        # Use organization info contained in entity to create an organization in Apinf
        try:
            apinf_id = self._client.create_organization(entity.display_name, url, entity.description)

            # Save the id given in apinf for the organization
            entity.extras['apinf_id'] = apinf_id

            # Include extras managed by Apinf in order to simplify providing this info
            entity.extras['url'] = url
            entity.extras['contact_name'] = ''
            entity.extras['contact_email'] = ''
            entity.extras['contact_phone'] = ''
            entity.save()
        except AuthenticationError as e:
            # Display a warning message
            toolkit.c.errors = unicode(e)

    # IResourceController
    def _include_apinf_url(self, resource):
        if resource['upload'] == '':
            # Get URL of the API description
            self._client = ApinfClient()
            apinf_url = self._client.get_apinf_page(resource['url'])

            if apinf_url is not None:
                resource['apinf_page'] = apinf_url

        return resource

    def before_create(self, context, resource):
        return self._include_apinf_url(resource)

    def before_update(self, context, current, resource):
        # Check if the URL of the resource has changed
        if current['url'] != resource['url']:
            resource = self._include_apinf_url(resource)

        return resource

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'apinf_resources')
