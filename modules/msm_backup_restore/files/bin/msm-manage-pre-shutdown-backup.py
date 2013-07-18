#!/usr/bin/env python
"""
Authorize and manage the running of pre-shutdown backup script.

It should only run if the instance is in the 'shutting down' state.
If this kicks off the pre-shutdown backup script, it will
notify the DB and Memcache about the state changes:

Instance States:
    'backup started'
    'backup finished'

"""
import bmemcached
import json
import os
import re
import requests
import subprocess
import sys
import time

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Exit early if DATABASE_URL env var is not set.
db_url = os.getenv('DATABASE_URL', None)
if not db_url:
    sys.exit(1)

# Convert from Heroku style DATABASE_URL to Sqlalchemy style, if necessary
DATABASE_URL = re.sub('^postgres:', 'postgresql:', db_url)

engine = create_engine(DATABASE_URL, poolclass=NullPool)
Base = declarative_base(engine)

class Instance(Base):
    """"""
    __tablename__ = 'launcher_instance'
    __table_args__ = {'autoload':True}

def loadSession():
    """"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def get_instance_id():
    """Use EC2 metadata to get instance id."""
    response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
    return response.text

def authorize_backup(session=None):
    if not session:
        session = loadSession()
    authorized = False
    instance_name = get_instance_id()
    instance = (session.query(Instance).
                filter(Instance.name == instance_name).
                one()
               )
    if instance.state == 'shutting down':
        authorized = True
    return authorized

def update_db(value, session=None):
    if not session:
        session = loadSession()
    instance_name = get_instance_id()
    instance = (session.query(Instance).
                filter(Instance.name == instance_name).
                one()
               )
    instance.state = value
    session.commit()
    session.close()

def memcache_client():
    client = None
    servers =  os.getenv('MEMCACHIER_SERVERS', None)
    username = os.getenv('MEMCACHIER_USERNAME', None)
    password = os.getenv('MEMCACHIER_PASSWORD', None)

    if all([servers, username, password]):
        client = bmemcached.Client((servers, ), username, password)
    return client

def make_key(key, key_prefix, version):
    return ':'.join([key_prefix, str(version), key])

def update_memcache(value):
    cache = memcache_client()
    key = make_key('instance_state', '', 1)
    value_js = json.dumps(['instance_state', value])
    timeout = int(time.time()) + 60*60*24*365  # One year from now
    cache.set(key, value_js, timeout)

def main():
    session = loadSession()
    if authorize_backup(session):
        update_db('backup started', session)
        update_memcache('backup started')

        cmd = ['/usr/local/bin/msm-pre-shutdown-backup.sh']
        subprocess.call(cmd)

        update_db('backup finished')
        update_memcache('backup finished')


if __name__ == "__main__":
    main()
