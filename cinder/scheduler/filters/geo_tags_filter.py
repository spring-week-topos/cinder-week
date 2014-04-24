# Copyright (c) 2014 Intel
# All Rights Reserved.
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

from cinder import db

from cinder.openstack.common import jsonutils
from cinder.openstack.common import log as logging
from cinder.openstack.common.scheduler import filters


LOG = logging.getLogger(__name__)


class GeoTagsFilter(filters.BaseHostFilter):
    """GeoTags Filter."""

    def _is_valid_rack_loc(self, host_rack, wanted_rack):
        wanted = wanted_rack.split('-')
        host = host_rack.split('-')
        if not wanted[-1]:
            wanted.pop()
        rack_aff = zip(wanted, host)
        for x, v in rack_aff:
            #may be empty due to to split
            if x != v:
                return False
        return True

    def host_passes(self, host_state, filter_properties):
        """Return True if host has sufficient capacity."""
        #(licostan): Add geotag data to the host_state instead of
        #querying it...
        #TODO: add scheduler hints to cinder.
        metadata_hints = filter_properties.get('metadata') or {}
        context = filter_properties['context']

        try:
            gt_hints = jsonutils.loads(metadata_hints.get('geo_tags',
                                                          '{}'))
        except Exception as e:
            LOG.error('Cannot parse json gtags %s' % gt_hints)
            return False

        #for non geo tags servers
        geo_tag = db.geo_tag_get_by_node_name(context, host_state.host)
        if not geo_tag:
            LOG.info('NO GEO TAG FOUND FOR %s' % host_state.host)
            return True

        #do other geotags check here based on gt-hints
        if geo_tag['valid_invalid'].lower() != 'valid':
            LOG.info('GEO TAG Invalid for %s' % host_state.host)
            return False

        wanted_rack = gt_hints.get('rack_location', None)
        host_loc = geo_tag.get('loc_or_error_msg')
        if wanted_rack and not self._is_valid_rack_loc(host_loc, wanted_rack):
            LOG.info('Invalid rack location wanted: %(want)s '
                     ' host_loc: %(host_loc)s' % {'want': wanted_rack,
                                                  'host_loc': host_loc})
            return False

        LOG.info('GEO TAG VALID FOR  %s' % host_state.host)
        return True
