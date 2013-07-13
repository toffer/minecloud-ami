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

class Environ(object):
    """
    Lookup values from environment or from file.

    For scripts that require environment variables, but are
    run from init.d (which does not set env vars defined in
    '/etc/environment'), Environ provides a way to read variable
    values directly from a file if they aren't already present in
    environment.

    Environment file must be in /etc/environment format:

    KEY1=value1
    KEY2=value2
    ...

    """
    def __init__(self, env_filename='/etc/environment'):
        self._env_vars = {}
        self._parse_environment_file(env_filename)

    def _parse_environment_file(self, filename):
        with open(filename, 'r') as f:
            for line in f:
                key, val = [x.strip() for x in line.split('=')]
                self._env_vars[key] = val

    def get(self, key):
        env_var = os.getenv(key, None)
        if not env_var:
            env_var = self._env_vars.get(key, None)
        return env_var

    def key_val(self, key):
        return "%s=%s" % (key, self.get(key))

ENVIRON = Environ()

# Convert from Heroku style DATABASE_URL to Sqlalchemy style, if necessary
db_url = ENVIRON.get('DATABASE_URL')
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
    servers = ENVIRON.get('MEMCACHIER_SERVERS')
    username = ENVIRON.get('MEMCACHIER_USERNAME')
    password = ENVIRON.get('MEMCACHIER_PASSWORD')

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

        aws_key = ENVIRON.key_val('AWS_ACCESS_KEY_ID')
        aws_secret = ENVIRON.key_val('AWS_SECRET_ACCESS_KEY')
        s3_bucket = ENVIRON.key_val('MSM_S3_BUCKET')

        cmd_args = ['/usr/bin/env', aws_key, aws_secret, s3_bucket,
                    '/usr/local/bin/msm-pre-shutdown-backup.sh']
        subprocess.call(cmd_args)

        update_db('backup finished')
        update_memcache('backup finished')


if __name__ == "__main__":
    main()
