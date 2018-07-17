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

from ckan.lib.plugins import DefaultOrganizationForm
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from apinf.apinf_client import ApinfClient
from errors import AuthenticationError


class Apinf_ResourcesPlugin(plugins.SingletonPlugin, DefaultOrganizationForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IOrganizationController, inherit=True)
    plugins.implements(plugins.IGroupForm, inherit=True)

    def __init__(self, name=None):
        self._client = ApinfClient()

    # IGroupForm - Organizations Form
    def group_types(self):
        return ('organization',)

    def group_controller(self):
        return 'organization'

    def form_to_db_schema(self):
        schema = super(Apinf_ResourcesPlugin, self).form_to_db_schema()

        if schema is None:
            schema = {}

        # Update schema with Apinf organization fields
        validators = [toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras')]

        schema.update({
            'url': [toolkit.get_validator('not_empty'), toolkit.get_validator('url_validator'), toolkit.get_converter('convert_to_extras')],
            'contact_name': validators,
            'contact_email': [toolkit.get_validator('ignore_missing'), toolkit.get_validator('email_validator'), toolkit.get_converter('convert_to_extras')],
            'contact_phone': validators
        })

        return schema

    def validate(self, context, data_dict, schema, action):
        data, errors = toolkit.navl_validate(data_dict, schema, context)
        if action == 'organization_show':
            # Transform Apinf fields saved as extras into Organization object fields
            extras = ['url', 'contact_name', 'contact_email', 'contact_phone']

            effective_extras = []
            for extra in data_dict['extras']:
                if extra['key'] in extras:
                    data[extra['key']] = extra['value']
                else:
                    effective_extras.append(extra)

            data['extras'] = effective_extras

        return data, errors

    # IOrganizationController
    def _create_organization(self, entity):
        # Use organization info contained in entity to create an organization in Apinf
        try:
            apinf_id = self._client.create_organization(
                entity.display_name, entity.description, entity.url, entity.contact_name, entity.contact_email, entity.contact_phone)

            # Save the id given in apinf for the organization
            entity.extras['apinf_id'] = apinf_id
            entity.save()
        except AuthenticationError as e:
            # Display a warning message
            toolkit.c.errors = unicode(e)

    def create(self, entity):
        self._create_organization(entity)

    def edit(self, entity):
        # Check if the organization is already published in Apinf
        if 'apinf_id' not in entity.extras:
            # TODO: Handle user deleting this property for a published organization
            self._create_organization(entity)

        else:
            try:
                self._client.update_organization(
                    entity.extras['apinf_id'], entity.display_name, entity.description, entity.url, entity.contact_name, entity.contact_email, entity.contact_phone)

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
