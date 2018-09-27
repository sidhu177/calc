#! /bin/sh

set -e

echo "----- Clearing Python cache -----"
# https://stackoverflow.com/a/30659970
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

echo "----- Updating Python Dependencies -----"
python -m pip install -r requirements-dev.txt

echo "----- Updating Node Dependencies -----"
yarn

echo "----- Migrating Database -----"
python manage.py migrate --noinput

echo "----- Updating search field -----"
python manage.py update_search_field

echo "----- Initializing Groups -----"
python manage.py initgroups

if [ -n "${CALC_IS_ON_DOCKER_IN_CLOUD}" ]; then
  echo "----- Building Static Assets -----"
  gulp build
fi
