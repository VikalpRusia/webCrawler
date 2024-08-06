#! /usr/bin/env sh

# safety switch, exit script if there's error. Full command of shortcut `set -e`
set -o errexit
# safety switch, uninitialized variables will stop script. Full command of shortcut `set -u`
set -o nounset

# replace the celery constants from the env variables
sed -i "/CACHE_EXPIRY =/ c CACHE_EXPIRY = ${CACHE_EXPIRY}" /app/config/constants.py
sed -i '/REDIS_HOST =/ c REDIS_HOST = \"'${REDIS_HOST}'\"' /app/config/constants.py
