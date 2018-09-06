#! /bin/bash

set -e

export $(cat .env.cloudgov-proxy | xargs)

if [ -z "$1" ]; then
  echo "Usage: $0 <instance-name>"
  echo
  echo "This will:"
  echo
  echo "  * create a new nginx.conf that proxies to <instance-name>;"
  echo "  * set the site domain on the remote machine called <instance-name>."
  exit 1
fi

if [ -n "$COMPOSE_FILE" ]
then
  echo "Please run this command in a new terminal session."
  exit 1
fi

cd ..

echo "Activating $1..."

source activate-$1

echo "Creating nginx.conf..."

cd cloudgov-proxy

sed 's/\${DOCKER_HOST_IP}/'${DOCKER_HOST_IP}/ nginx.conf.template > \
  nginx.conf

cd ..

echo "Setting site domain on $1..."

python manage.py shell <<DOC
from django.contrib.sites.models import Site

s = Site.objects.get_current()

print("Old site was", s)

s.domain = "${CF_APP}.app.cloud.gov"
s.name = 'CALC (price list analysis branch)'

print("New site is", s)

s.save()

exit
DOC

echo "Done."
