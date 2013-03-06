#!/bin/sh

# Restore working files from S3.

BOTO_RSYNC='/usr/local/venv/bin/boto-rsync'

# S3 Bucket Name is found in global environmental 
# variable (MSM_S3_BUCKET), or as positional arg.
if [ -n "${MSM_S3_BUCKET}" ]; then
    S3_BUCKET=$MSM_S3_BUCKET
elif [ -z "${MSM_S3_BUCKET}" ] && [ $# -eq 1 ]; then
    S3_BUCKET=$1
else
    printf "Usage: %s <s3_bucket_name> \n" $0
    exit 2
fi

# Delete
rm -rf /opt/msm/jars
rm -rf /opt/msm/versioning
rm -rf /opt/msm/servers

# Download files
$BOTO_RSYNC s3://$S3_BUCKET/opt/msm/jars /opt/msm/jars
$BOTO_RSYNC s3://$S3_BUCKET/opt/msm/versioning /opt/msm/versioning
$BOTO_RSYNC s3://$S3_BUCKET/opt/msm/servers /opt/msm/servers

# Fix permissions
chown -R minecraft:minecraft /opt/msm/
