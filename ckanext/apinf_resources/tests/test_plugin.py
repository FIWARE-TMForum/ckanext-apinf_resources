from __future__ import unicode_literals

import unittest
from mock import MagicMock
from parameterized import parameterized

import ckanext.apinf_resources.plugin as plugin


class PluginTestCase(unittest.TestCase):

    def setUp(self):
        self._apinf_client = MagicMock()
        plugin.ApinfClient = MagicMock(return_value=self._apinf_client)

    def test_load_config(self):
        plugin.toolkit = MagicMock()
        config = {}

        plugin_instance = plugin.Apinf_ResourcesPlugin()
        plugin_instance.update_config(config)

        plugin.toolkit.add_template_directory.assert_called_once_with(config, 'templates')
        plugin.toolkit.add_public_directory.assert_called_once_with(config, 'public')
        plugin.toolkit.add_resource.assert_called_once_with('fanstatic', 'apinf_resources')

    @parameterized.expand([
        ('file', {'upload': 'file', 'apinf_page': ''}, '', None),
        ('url_apinf', {'upload': '', 'apinf_page': '', 'url': 'http://service.com/'}, 'http://apinfsite/', 'http://apinfsite/'),
        ('url_not_published', {'upload': '', 'apinf_page': '', 'url': 'http://service.com/'}, '', None)
    ])
    def test_before_create(self, name, resource, exp_apinf, val_apinf):
        context = {}
        self._apinf_client.get_apinf_page.return_value = val_apinf

        plugin_instance = plugin.Apinf_ResourcesPlugin()
        res = plugin_instance.before_create(context, resource)

        self.assertEquals(resource, res)
        self.assertEquals(exp_apinf, resource['apinf_page'])

        if resource['upload'] == '':
            self._apinf_client.get_apinf_page.assert_called_once_with(resource['url'])
        else:
            self.assertEquals(0, self._apinf_client.get_apinf_page.call_count)

    @parameterized.expand([
        ('changed', {'upload': '', 'url': 'http://service.com/', 'apinf_page': 'http://apinfsite/'},
         {'url': 'http://newservice.com/'}, 'http://newapinfsite/', 'http://newapinfsite/'),
        ('not_changed', {'upload': '', 'url': 'http://service.com/', 'apinf_page': 'http://apinfsite/'},
         {'url': 'http://service.com/'}, 'http://apinfsite/', None)
    ])
    def test_before_update(self, name, resource, current, exp_apinf, val_apinf):
        context = {}
        self._apinf_client.get_apinf_page.return_value = val_apinf

        plugin_instance = plugin.Apinf_ResourcesPlugin()
        res = plugin_instance.before_update(context, current, resource)

        self.assertEquals(resource, res)
        self.assertEquals(exp_apinf, resource['apinf_page'])

        if val_apinf is not None:
            self._apinf_client.get_apinf_page.assert_called_once_with(resource['url'])
        else:
            self.assertEquals(0, self._apinf_client.get_apinf_page.call_count)
