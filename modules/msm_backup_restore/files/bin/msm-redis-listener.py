#!/usr/bin/env python

import os
import redis
import subprocess


def main():
    redis_url = os.getenv('REDISTOGO_URL')
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