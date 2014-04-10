
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
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import UniqueConstraint


def upgrade(engine):
    meta = MetaData()
    meta.bind = engine
    geo_tag_uc_name = 'uniq_node_name_geotag'
    geo_tags = Table('services_geotag', meta,
                     Column('created_at', DateTime(timezone=False)),
                     Column('updated_at', DateTime(timezone=False)),
                     Column('deleted_at', DateTime(timezone=False)),
                     Column('deleted', Integer, default=0),
                     Column('id', Integer, primary_key=True),
                     Column('server_name', String(255), nullable=False),
                     Column('ip_address', String(39)),
                     Column('mac_address', String(17)),
                     Column('parent_mac', String(17)),
                     Column('time_data_rec', String(28)),
                     Column('rfid', String(24)),
                     Column('rfid_signature', String(10)),
                     Column('plt_longitude', String(11)),
                     Column('plt_latitude', String(11)),
                     Column('loc_or_error_msg', String(17)),
                     Column('valid_invalid', String(7)),
                     Column('rfid_scan_time', String(19)),
                     Column('rfid_rec_time', String(19)),
                     Column('geo_loc_valid_time', String(19)),
                     Column('geo_loc_invalid_time', String(19)),
                     Column('secure_geo_loc', String(10)),
                     Column('auto_geo_loc', String(10)),
                     Column('cable_disc_prd', String(10)),
                     Column('geo_loc_server', String(5)),
                     Column('node_manager', String(5)),
                     Column('platform_guid', String(32)),
                     Column('geo_loc_svr_guid', String(32)),
                     Column('rfid_reader_guid', String(32)),
                     Column('alerts', Integer),
                     Index('compute_name_gt_tag_valid_idx',
                           'server_name', 'valid_invalid'),
                     UniqueConstraint('server_name', name=geo_tag_uc_name),
                     mysql_engine='InnoDB',
                     mysql_charset='utf8')

    geo_tags.create()


def downgrade(engine):
    pass
