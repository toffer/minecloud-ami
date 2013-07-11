#!/usr/bin/env python

import os
import re
import redis
import subprocess
import sys

def get_redis_url():
    """Get redis url from env var, or read it from /etc/environment."""
    url = os.getenv('REDISTOGO_URL', None)
    if not url:
        with open('/etc/environment', 'r') as f:
            for line in f:
                match = re.match(r'^REDISTOGO_URL=(.*)', line)
                if match:
                    url = match.group(1)
    return url

def main():
    redis_url = get_redis_url()
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