#!/usr/bin/env python

import os
import re
import redis
import subprocess
import sys

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

    def get(self, var_name):
        env_var = os.getenv(var_name, None)
        if not env_var:
            env_var = self._env_vars.get(var_name, None)
        return env_var


def main():
    environ = Environ()
    redis_url = environ.get('REDISTOGO_URL')
    if not redis_url:
        sys.exit(1)

    conn = redis.StrictRedis.from_url(redis_url)
    subscriber = conn.pubsub()
    subscriber.subscribe('command')

    backup_cmd = ['/usr/local/venv/bin/python',
                  '/usr/local/bin/msm-manage-pre-shutdown-backup.py'
                 ]

    for msg in subscriber.listen():
        if msg['type'] == "message" and msg['data'] == 'backup':
            subprocess.call(backup_cmd)


if __name__ == '__main__':
    main()