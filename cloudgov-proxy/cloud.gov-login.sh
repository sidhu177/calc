#! /bin/sh

set -e

export $(cat .env.cloudgov-proxy | xargs)

open https://login.fr.cloud.gov/passcode

cf login -a api.fr.cloud.gov --sso -o ${CF_ORG} -s ${CF_SPACE}
