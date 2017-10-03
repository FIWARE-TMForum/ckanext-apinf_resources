from __future__ import unicode_literals

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class Apinf_ResourcesPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IResourceController)

    def _include_apinf_url(self, resource):
        # Get URL of the API description
        # Include the new URL as mete info
        pass

    # IResourceController
    def before_create(self, context, resource):
        # Check if the resource is a URL resource
        pass

    def before_update(self, context, current, resource):
        # Check if the URL of the resource has changed
        pass

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'apinf_resources')