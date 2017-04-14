#!/bin/bash

set -e

if [ $CF_INSTANCE_INDEX = "0" ]; then
    echo "----- Migrating Database -----"
    python manage.py migrate --noinput

    echo "----- Updating search field -----"
    # The '-W ignore is to suppress https://github.com/18F/calc/issues/291.
    python -W ignore manage.py update_search_field contracts Contract

    echo "----- Initializing Groups -----"
    python manage.py initgroups
fi
echo "------ Starting APP ------"
gunicorn hourglass.wsgi:application
