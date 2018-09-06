#! /bin/bash

set -e

export $(cat .env.cloudgov-proxy | xargs)

if [ -n "$COMPOSE_FILE" ]
then
  echo "Please run this command in a new terminal session."
  exit 1
fi

# Rebuild our Docker image and tag it.
docker-compose build

# Push the newly-created image to Docker Hub.
docker-compose push

# Tell Cloud Foundry to push the Docker image on Docker Hub to our
# cloud.gov app. For more details on this functionality, see:
#
#   https://cloud.gov/docs/apps/experimental/docker/
#
# We're using `-u none` to disable health checks, which don't seem to
# work with CloudFoundry + nginx:
#
#   https://github.com/pivotal-cf/pcfdev/issues/27

cf push ${CF_APP} -o ${DOCKER_HUB_IMAGE} -m 64M -u none

echo "Push complete. Your site should be live at"
echo "https://${CF_APP}.app.cloud.gov."
