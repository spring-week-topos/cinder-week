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
from cinder.openstack.common import log as logging
from cinder.openstack.common.scheduler import filters


LOG = logging.getLogger(__name__)


class GeoTagsFilter(filters.BaseHostFilter):
    """GeoTags Filter."""

    def host_passes(self, host_state, filter_properties):
        """Return True if host has sufficient capacity."""
        #(licostan): Add geotag data to the host_state instead of
        #querying it...
        #TODO: add scheduler hints to cinder.
        metadata_hints = filter_properties.get('metadata') or {}
        gt_hints = metadata_hints.get('geo_tags', None)
        context = filter_properties['context']

        geo_tag = db.geo_tag_get_by_node_name(context, host_state.host)
        if not geo_tag:
            LOG.info('NO GEO TAG FOUND FOR %s' % host_state.host)
            return True
        #do other geotags check here based on gt-hints
        if geo_tag.valid_invalid.lower() == 'valid':
            LOG.info('GEO TAG FOUND FOR %s' % host_state.host)
            return True

        LOG.info('GEO TAG INVALID FOR  %s' % host_state.host)
        return False
