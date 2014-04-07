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

"""The GeoTag API extension."""

import datetime
from oslo.config import cfg

from webob import exc
from cinder.api import extensions
from cinder.api.openstack import wsgi
from cinder import db
from cinder import exception
from cinder.openstack.common import log as logging
from cinder.openstack.common import strutils
from cinder import rpc
from cinder import volume

CONF = cfg.CONF
LOG = logging.getLogger(__name__)
#(licostan): change to right policy and add it to policy file
authorize = extensions.extension_authorizer('volume', 'services')


def _get_context(req):
    return req.environ['cinder.context']


class GeoTagsController(object):
    """The GeoTag API controller for the OpenStack API."""
    allowed_keys = ['plt_longitude', 'plt_latitude', 'valid_invalid']
    
    def __init__(self):
        super(GeoTagsController, self).__init__()

    def _check_keys(self, values):
        for key in values.keys():
            if key not in self.allowed_keys:
                raise exc.HTTPBadRequest(explanation="Invalid keys")

    def index(self, req):
        """Returns all geo tags."""
        context = _get_context(req)
        authorize(context)
        filters = None
        if 'host' in req.GET:
            filters = {'host': req.GET['host']}
        gt = db.geo_tag_get_all(context, filters)
        return {'geo_tags': [g for g in gt]}

    def create(self, req, body):
        """Creates a geotag
        """
        context = _get_context(req)
        authorize(context)

        if len(body) != 1:
            raise exc.HTTPBadRequest()

        try:
            geo_tag = body['geo_tag']
            compute_name = geo_tag.pop("compute_name")
        except KeyError:
            raise exc.HTTPBadRequest()
        
        self._check_keys(geo_tag)
        try:
            db.service_get_by_host_and_topic(context, compute_name, CONF.volume_topic)
        except exception.ServiceNotFound:
            raise exc.HTTPNotFound(explanation=_("Host not found"))
                                                                                                                                                         
        try:
            #(licostan) only in this case we add it again..
            #need to adapt this to a proper db api for cinder...
            geo_tag['server_name'] = compute_name
            gt = db.geo_tag_create(context, geo_tag)
        except exception.GeoTagExists as e:
            LOG.info(e)
            raise exc.HTTPConflict()
        except exception.HostNotFound as e:
            msg = _('Host %(host)s do not exists') % {'host': compute_name}
            LOG.info(msg)
            raise exc.HTTPNotFound(explanation=e.format_message())

        return {'geo_tag': gt}

    def show(self, req, id):
        """Shows details of GeoTag."""
        context = _get_context(req)
        authorize(context)
        try:
            geo_tag = db.geo_tag_get_by_id_or_node_name(context, id)
        except exception.AggregateNotFound:
            LOG.info(_("Cannot shw GeoTag:  %s"), id)
            raise exc.HTTPNotFound()
        
        return {'geo_tag': geo_tag}
        
    def update(self, req, id, body):
        """Update geotag by server_name right now.
           id  == server_name 
        """
    
        context = _get_context(req)
        authorize(context)
    
        if len(body) != 1:
            raise exc.HTTPBadRequest()
        try:
            update_values = body["geo_tag"]
        except KeyError:
            raise exc.HTTPBadRequest()

        if len(update_values) < 1:
            raise exc.HTTPBadRequest()
        #(licostan): iteraate update_values and check valid_keys if not
        #throw error
        self._check_keys(update_values)
         #(licostan): remove compute_name and pass **update_values
         #to remove args
        try:
            geo_tag = db.geo_tag_update(context, id, update_values)
        except exception.NotFound as e:
            LOG.info(_('Cannot update geotag'))
            raise exc.HTTPNotFound(explanation=e.format_message())

        return {'geo_tag': geo_tag}
        
    def delete(self, req, id):
        """Removes a GeoTag by id/servername."""
        context = _get_context(req)
        authorize(context)
        try:
            db.geo_tag_destroy(context, id)
        except exception.NotFound:
            LOG.info(_('Cannot delete GeoTag: %s'), id)
            raise exc.HTTPNotFound()


class Geo_tags(extensions.ExtensionDescriptor):
    """Admin-only geo tags administration."""

    name = "Geo Tags"
    alias = "os-geo-tags"
    namespace = "http://docs.openstack.org/compute/ext/os-geo-tags/api/v1.1"
    updated = "2012-01-12T00:00:00+00:00"

    def get_resources(self):
        resources = []
        res = extensions.ResourceExtension('os-geo-tags',
                GeoTagsController())
        resources.append(res)
        return resources
