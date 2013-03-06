#!/usr/bin/env python

# Backup all MSM working files to S3.

# The "working files" are the current working files for the Minecraft
# server, located in /opt/msm/. They are rsync'ed from S3 upon
# server start up and rsync'ed back to S3 at periodic intervals, 
# as well as at server shutdown.
#
# This script ensures that the working files remain in a consistent
# state during the backup to S3, even if the Minecraft server is
# running and is actively being used.

import os
import psutil
import signal
import subprocess
import sys
import time

# Commands
MSM='/usr/local/bin/msm'
BOTO_RSYNC='/usr/local/venv/bin/boto-rsync'
S3_PUT='/usr/local/venv/bin/s3put'

def subprocess_setup():
    # Python installs a SIGPIPE handler by default. This is usually not what
    # non-Python subprocesses expect.
    # http://www.chiark.greenend.org.uk/ucgi/~cjwatson/blosxom/2009-07-02-python-sigpipe.html
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def running_servers():
    """Return list of running MSM server names."""
    all_procs = psutil.process_iter()
    mc_cmdlines= [proc.cmdline for proc in all_procs
                               if proc.username == 'minecraft'
                               if proc.name == 'screen'
                               if 'java' in proc.cmdline]
    servers = [segment.split('-')[1] for cmdline in mc_cmdlines
                                     for segment in cmdline
                                     if segment.find('msm-') > -1]
    return servers

def pre_backup(servers):
    """Ensure consistent state of Minecraft files before backup."""
    for server in servers:
        subprocess.call([MSM, server, 'save', 'off'])
        subprocess.call([MSM, server, 'save', 'all'])
        time.sleep(5)
        proc = subprocess.Popen([MSM, server, 'worlds', 'todisk'],
                                stdout=subprocess.PIPE,
                                preexec_fn=subprocess_setup)
        output = proc.communicate()[0]
        time.sleep(5)

def post_backup(servers):
    """Minecraft can resume saving to filesystem."""
    for server in servers:
        subprocess.call([MSM, server, 'save', 'on']) 
    
def backup():
    """Save working files to S3."""
    # Use s3put on /servers, to make sure all changed data files
    # get pushed to S3.
    path = os.path.join(SRC_DIR, 'servers')
    subprocess.call([S3_PUT, '--bucket', BUCKET, path])

    # Call boto-rsync on /servers also to delete old files
    # in S3 that are no longer on server.
    for directory in ['jars', 'versioning', 'servers']:
        src = os.path.join(SRC_DIR, directory)
        dst = os.path.join(DST_DIR, directory)
        subprocess.call([BOTO_RSYNC, '--verbose', '--delete', src, dst])

def main():
    servers = running_servers()
    if servers:
        pre_backup(servers)
        backup()
        post_backup(servers)
    else:
        backup()


if __name__ == "__main__":
    # Get required arg to set directory variables.
    if os.environ.get('MSM_S3_BUCKET'):
        BUCKET = os.environ.get('MSM_S3_BUCKET')
    elif len(sys.argv[1:]) == 1:
        BUCKET = sys.argv[1]
    else:
        print "Usage: %s <s3_bucket_name>" % sys.argv[0]
        sys.exit(1)

    BOTO_PREFIX = "s3://%s" % BUCKET
    SRC_DIR = os.path.join(os.sep, 'opt', 'msm')
    DST_DIR = os.path.join(BOTO_PREFIX, 'opt', 'msm')
    
    main()
