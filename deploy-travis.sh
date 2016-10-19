set -e

API="https://api.cloud.gov"
ORG="oasis"
SPACE="calc-dev"
APP_NAME="calc-dev"
MANIFEST="manifests/manifest-dev.yml"

# CF_USER and CF_PASSWORD are defined as private Environment Variables
# in the Travis web UI: https://travis-ci.org/18F/calc/settings
cf login -a $API -u $CF_USER -p $CF_PASSWORD -o $ORG -s $SPACE
cf zero-downtime-push $APP_NAME -f $MANIFEST
