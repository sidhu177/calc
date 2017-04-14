#! /bin/sh

set -e

echo "----- Updating Python Dependencies -----"
pip install -r requirements-dev.txt

echo "----- Updating Node Dependencies -----"
yarn

echo "----- Migrating Database -----"
python manage.py migrate --noinput

echo "----- Updating search field -----"
# The '-W ignore is to suppress https://github.com/18F/calc/issues/291.
python -W ignore manage.py update_search_field contracts Contract

echo "----- Initializing Groups -----"
python manage.py initgroups

if [ -n "${CALC_IS_ON_DOCKER_IN_CLOUD}" ]; then
  echo "----- Building Static Assets -----"
  gulp build
fi
