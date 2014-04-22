# Copyright (c) 2014 Rackspace Hosting
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


from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Text

from nova.openstack.common import timeutils


def upgrade(engine):
    meta = MetaData()
    meta.bind = engine

    # Add a new power_state column to geo tags 
    table_name = 'services_geotag'
    table = Table(table_name, meta, autoload=True)
    stats = Column('power_state', String(50), default=None)
    table.create_column(stats)


def downgrade(engine):
    meta = MetaData()
    meta.bind = engine

    table_names = 'services_geotag'
    table = Table(table_name, meta, autoload=True)
    table.drop_column('power_state')
    
    