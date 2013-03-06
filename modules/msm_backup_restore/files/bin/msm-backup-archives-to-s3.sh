#!/bin/sh

# Backup MSM archives to S3.

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

# Backup MSM servers to /opt/msm/archives/
/usr/local/bin/msm all backup

# Backup worlds to /opt/msm/archives/
/usr/local/bin/msm all worlds backup

# Backup /opt/msm/archives to S3
$BOTO_RSYNC /opt/msm/archives/ s3://$S3_BUCKET/opt/msm/archives
