from __future__ import unicode_literals

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from apinf.apinf_client import ApinfClient


class Apinf_ResourcesPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IResourceController, inherit=True)

    def _include_apinf_url(self, resource):
        if resource['upload'] == '':
            # Get URL of the API description
            client = ApinfClient()
            apinf_url = client.get_apinf_page(resource['url'])

            if apinf_url is not None:
                resource['apinf_page'] = apinf_url

        return resource

    # IResourceController
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
