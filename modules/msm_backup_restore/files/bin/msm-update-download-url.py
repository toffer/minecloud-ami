#!/usr/bin/env python

# Temporary fix to make sure that we download the latest minecraft
# server until the msm script handles it by itself.
#
# Note the hard-coded target file.

import json
import urllib2

MINECRAFT_VERSION_URL = 'http://s3.amazonaws.com/Minecraft.Download/versions/versions.json'
TARGET_FILE = '/opt/msm/jars/minecraft/target.txt'

def get_version():
    response = urllib2.urlopen(MINECRAFT_VERSION_URL)
    obj = json.loads(response.read())
    version = obj['latest']['release']
    return version

def make_url(version):
    url = ("https://s3.amazonaws.com/Minecraft.Download/"
           "versions/{0}/minecraft_server.{0}.jar".format(version))
    return url

def main():
    version = get_version()
    url = make_url(version)
    with open(TARGET_FILE, 'w') as f:
        f.write(url + '\n')

if __name__ == '__main__':
    main()