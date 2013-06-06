#!/bin/sh

# Shutdown msm and run complete backup to S3.

# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and
# MSM_S3_BUCKET should be set as environment variables.

MSM='/usr/local/bin/msm'
VENV_PYTHON='/usr/local/venv/bin/python'

# Shutdown msm
$MSM stop

# Logroll
$MSM all logroll
find /opt/msm/servers -name 'server.log.offset' -exec rm '{}' ';'

# Backup working files
BACKUP_WORKING_FILES=/usr/local/bin/msm-backup-working-files-to-s3.py
if [ -x $VENV_PYTHON ] && [ -x $BACKUP_WORKING_FILES ]; then
    $VENV_PYTHON $BACKUP_WORKING_FILES $MSM_S3_BUCKET
fi

# Backup archives
BACKUP_ARCHIVES=/usr/local/bin/msm-backup-archives-to-s3.sh
if [ -x $VENV_PYTHON ] && [ -x $BACKUP_ARCHIVES ]; then
    $BACKUP_ARCHIVES $MSM_S3_BUCKET
fi

