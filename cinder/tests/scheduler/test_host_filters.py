# Copyright 2011 OpenStack Foundation  # All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
Tests For Scheduler Host Filters.
"""

import mock

from cinder import context
from cinder.openstack.common import jsonutils
from cinder.openstack.common.scheduler import filters
from cinder import test
from cinder.tests.scheduler import fakes


class HostFiltersTestCase(test.TestCase):
    """Test case for host filters."""

    def setUp(self):
        super(HostFiltersTestCase, self).setUp()
        self.context = context.RequestContext('fake', 'fake')
        self.json_query = jsonutils.dumps(
            ['and',
                ['>=', '$free_capacity_gb', 1024],
                ['>=', '$total_capacity_gb', 10 * 1024]])
        # This has a side effect of testing 'get_filter_classes'
        # when specifying a method (in this case, our standard filters)
        filter_handler = filters.HostFilterHandler('cinder.scheduler.filters')
        classes = filter_handler.get_all_classes()
        self.class_map = {}
        for cls in classes:
            self.class_map[cls.__name__] = cls

    @mock.patch('cinder.utils.service_is_up')
    def test_capacity_filter_passes(self, _mock_serv_is_up):
        _mock_serv_is_up.return_value = True
        filt_cls = self.class_map['CapacityFilter']()
        filter_properties = {'size': 100}
        service = {'disabled': False}
        host = fakes.FakeHostState('host1',
                                   {'free_capacity_gb': 200,
                                    'updated_at': None,
                                    'service': service})
        self.assertTrue(filt_cls.host_passes(host, filter_properties))

    @mock.patch('cinder.utils.service_is_up')
    def test_capacity_filter_fails(self, _mock_serv_is_up):
        _mock_serv_is_up.return_value = True
        filt_cls = self.class_map['CapacityFilter']()
        filter_properties = {'size': 100}
        service = {'disabled': False}
        host = fakes.FakeHostState('host1',
                                   {'free_capacity_gb': 120,
                                    'reserved_percentage': 20,
                                    'updated_at': None,
                                    'service': service})
        self.assertFalse(filt_cls.host_passes(host, filter_properties))

    @mock.patch('cinder.utils.service_is_up')
    def test_capacity_filter_passes_infinite(self, _mock_serv_is_up):
        _mock_serv_is_up.return_value = True
        filt_cls = self.class_map['CapacityFilter']()
        filter_properties = {'size': 100}
        service = {'disabled': False}
        host = fakes.FakeHostState('host1',
                                   {'free_capacity_gb': 'infinite',
                                    'updated_at': None,
                                    'service': service})
        self.assertTrue(filt_cls.host_passes(host, filter_properties))

    @mock.patch('cinder.utils.service_is_up')
    def test_capacity_filter_passes_unknown(self, _mock_serv_is_up):
        _mock_serv_is_up.return_value = True
        filt_cls = self.class_map['CapacityFilter']()
        filter_properties = {'size': 100}
        service = {'disabled': False}
        host = fakes.FakeHostState('host1',
                                   {'free_capacity_gb': 'unknown',
                                    'updated_at': None,
                                    'service': service})
        self.assertTrue(filt_cls.host_passes(host, filter_properties))

    def _test_geo_tags_filter(self, gtag, wanted,
                              host_passes=False):
        geo_tag_mock = mock.Mock('cinder.db.geo_tag_get_by_node_name')
        geo_tag_mock.return_value = {'valid_invalid': 'Valid',
                                     'loc_or_error_msg': gtag}

        filt_cls = self.class_map['GeoTagsFilter']()
        host = fakes.FakeHostState('host1', {})

        wanted_tags = '{"rack_location": "%s"}' % wanted
        filter_properties = {'context': self.context.elevated(),
                             'metadata': {'geo_tags': wanted_tags}}
        if host_passes:
            self.assertTrue(filt_cls.host_passes(host, filter_properties))
        else:
            self.assertFalse(filt_cls.host_passes(host, filter_properties))

    def test_geo_tags_filter_valid_rack(self):
        ok_locations = ['1-2-3-4-5', '1-2-3-4', '1-2-3-4-',
                        '1-2-3', '1-2', '1-', '1']
        for x in ok_locations:
            self._test_geo_tags_filter('1-2-3-4-5', x, True)

    def test_geo_tags_filter_invalid_rack(self):
        ok_locations = ['1-2-3-4-3', '1-2-3-2', '1-2-3-1-',
                        '1-5-3', '3-2', '2-', '2']
        for x in ok_locations:
            self._test_geo_tags_filter('1-2-3-4-5', x, True)

    @mock.patch('cinder.db.geo_tag_get_by_node_name')
    def test_geo_tags_filter_no_list_passes(self, geo_tag_mock):
        geo_tag_mock.return_value = {'valid_invalid': 'Invalid'}

        filt_cls = self.class_map['GeoTagsFilter']()
        host = fakes.FakeHostState('host1', {})
        filter_properties = {'context': self.context.elevated()}
        self.assertFalse(filt_cls.host_passes(host, filter_properties))

    @mock.patch('cinder.db.geo_tag_get_by_node_name')
    def test_geo_tags_filter_valid_passes(self, geo_tag_mock):
        geo_tag_mock.return_value = {'valid_invalid': 'Valid'}

        filt_cls = self.class_map['GeoTagsFilter']()
        host = fakes.FakeHostState('host1', {})
        filter_properties = {'context': self.context.elevated()}
        self.assertTrue(filt_cls.host_passes(host, filter_properties))
