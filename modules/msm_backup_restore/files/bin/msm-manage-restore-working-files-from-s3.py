#!/usr/bin/env python

import boto
import os
import subprocess

def s3_bucket_contains_msm_dir(bucket):
    """Return True if bucket contains /opt/msm 'directory'."""
    conn = boto.connect_s3()
    bkt = conn.get_bucket(bucket)
    result_set = bkt.list(prefix='opt/msm')
    return len(list(result_set)) > 0

def main():
    bucket = os.getenv('MSM_S3_BUCKET')
    restore_script = '/usr/local/bin/msm-restore-working-files-from-s3.sh'

    if s3_bucket_contains_msm_dir(bucket):
        subprocess.call([restore_script])

if __name__ == '__main__':
    main()
