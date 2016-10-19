# Deploying to Cloud Foundry

**Only of interest to 18F team members**

Download the Cloud Foundry CLI according to the instructions here:
https://docs.cloud.gov/getting-started/setup/.
Make sure you are using a version >= v6.17.1, otherwise pushing multiple apps
at once might not work.

You will also need to install the `autopilot` plugin for Cloud Foundry, which
is used for zero-downtime deploys. Instructions are at https://github.com/contraband/autopilot.

To start, target the org and space you want to work with. For example, if you wanted to work with the staging space:
`cf target -o oasis -s calc-dev`

Manifest files, which contain import deploy configuration settings, are located
in the [manifests](manifests/) directory of this project.

Note that this project has two requirements files:
* `requirements.txt` for production dependencies
* `requirements-dev.txt` for development and testing dependencies

During local development and continuous integration testing, `pip install -r requirements-dev.txt` is used,
which installs both development and production dependencies.
During deployments, the Cloud Foundry python buildpack uses only `requirements.txt` by default,
so only production dependencies will be installed.

## CF Structure
- Organization: `oasis`
- Spaces: `calc-dev` (staging), `calc-prod` (production)
- Apps:
  - `calc-dev` (staging) space:
    - `calc-dev`
    - `calc-rqworker`
    - `calc-rqscheduler`
  - `calc-prod` (production) space:
    - `calc-prod`
    - `calc-rqworker`
    - `calc-rqscheduler`
    - `calc-maintenance`
- Routes:
  - calc-dev.apps.cloud.gov -> `calc-dev` space, `calc-dev` app
  - calc-prod.apps.cloud.gov -> `calc-prod` space, `calc-prod` app
  - calc.gsa.gov -> `calc-prod` space, `calc-prod` app
    or the maintenance page app, `calc-maintenance`

## Services

### User Provided Service

For cloud.gov deployments, this project makes use of a [User Provided Service (UPS)][UPS] to get its configuration
variables, instead of using the local environment (except for [New Relic-related environment variables](#new-relic-environment-variables)).
You will need to create a UPS called `calc-env`, provide 'credentials' to it, and link it to the
application instance. This will need to be done for every Cloud Foundry `space`.

First, create a JSON file (e.g. `credentials-staging.json`) with all the configuration values specified as per the "Environment Variables" section of [`README.md`][]. **DO NOT COMMIT THIS FILE.**

```json
{
  "SECRET_KEY": "my secret key",
  "...": "other environment variables"
}
```

Then enter the following commands (filling in the main application instance name
for `<APP_INSTANCE>`) to create the user-provided service:

```sh
cf cups calc-env -p credentials-staging.json
```

You can update the user-provided service with the following commands:

```sh
cf uups calc-env -p credentials-staging.json
cf restage calc-dev
```

### Database Service

CALC uses PostgreSQL for its database.

```sh
cf create-service aws-rds <SERVICE_PLAN> calc-db
```

(Don't know what `<SERVICE_PLAN>` to use? Try `cf marketplace`.)

### Redis Service

CALC uses Redis along with [rq](http://python-rq.org/) for scheduling and processing
asynchronous tasks.

```sh
cf create-service redis28-swarm standard calc-redis
```

## New Relic Environment Variables

Basic New Relic configuration is done in [`newrelic.ini`](/newrelic.ini), with
additional settings specified in each deployment environment's [manifest](/manifests/) file.

As described in [`README.md`](/README.md), you will need to supply the `NEW_RELIC_LICENSE_KEY`
as part of each deployment's [User Provided Service](#user-provided-service).

## Staging Server

The staging server updates automatically when changes are merged into the
`develop` branch. Check out the `deploy` section of [.travis.yml](.travis.yml)
for details and settings.

Should you need to, you can push directly to calc-dev.apps.cloud.gov with:

```sh
cf target -o oasis -s calc-dev
cf push -f manifests/manifest-staging.yml
```

## Your Own Server

If you want to deploy to your own sandbox, e.g. for the purpose of deploying a branch you're working on, see the wiki page on [How to Deploy to your Sandbox](https://github.com/18F/calc/wiki/How-to-Deploy-to-your-Sandbox).

There is an example sandbox manifest at [manifests/manifest-sandbox.yml](manifests/manifest-sandbox.yml)

## Production Servers

Production deploys are a somewhat manual process in that they are not done
from CI. However, just like in our Travis deployments to staging, we use the
Cloud Foundry [autopilot plugin](https://github.com/contraband/autopilot).

To deploy, first make sure you are targeting the prod space:

```sh
cf target -o oasis -s calc-prod
```

Now, if you don't already have the autopilot plugin, you can install it
by running:

```sh
cf install-plugin autopilot -f -r CF-Community
```

Then use the autopilot plugin's `zero-downtime-push` command to deploy:

```sh
cf zero-downtime-push calc-prod -f manifests/manifest-prod.yml
```

If a breaking database migration needs to be done, things get a little trickier because
the database service is actually shared between the two production apps. If the migration
breaks the current version of CALC, we'll need to have a (hopefully short) amount of downtime.

We have a very simple maintenance page application that uses the CloudFoundry staticfiles
buildpack. This app is is the [maintenance_page](maintenance_page/) subdirectory.

If `calc-maintenance` is not running or has not been deployed yet:

```sh
cd maintenance_page
cf push
```

Once `calc-maintenance` is running:

```sh
cf map-route calc-maintenance calc.gsa.gov
cf unmap-route calc-prod
```

And then deploy the production app:

```sh
cf push -f manifests/manifest-prod.yml
```

One the deploy is successful:

```sh
cf map-route calc-prod calc.gsa.gov
cf unmap-route calc-maintenance
```

## Logs

Logs in cloud.gov-deployed applications are generally viewable by running
`cf logs <APP_NAME> --recent`

Note that the web application and the `rq` worker application have separate
logs, so you will need to look at each individually.

## Initial Superuser

After the initial setup of `calc-db` and a production app, you will need to
create a superuser account, after which you'll be able to login to the
Django admin panel to add additional user accounts. The easiest way to create
the initial superuser is to use `cf-ssh` (docs [here](https://docs.cloud.gov/getting-started/one-off-tasks/))
and run `python manage.py createsuperuser`.

## Setting up the API

In production, CALC's public API is actually fronted by an [API Umbrella][]
instance on api.data.gov which proxies all API requests to CALC. This
allows CALC to not have to concern itself with details like API keys and
rate limiting.

In order to configure the proxying between api.data.gov and CALC,
you will need to obtain an administrative account on api.data.gov.
For more information on doing this, see the [api.data.gov User Manual][].

You'll then want to tell api.data.gov what host it will listen for, and
what host your API backend is listening on. For example:

| Frontend Host   | Backend Host   |
| --------------- | -------------- |
| api.data.gov    | calc.gsa.gov   |

You will also want to configure your API backend on
api.data.gov with one **Matching URL Prefixes** entry.
The **Backend Prefix** should always be `/api/`, while the
**Frontend Prefix** is up to you. Here's an example:

| Frontend Prefix | Backend Prefix |
| --------------- | -------------- |
| /gsa/calc/      | /api/          |

Now you'll need to configure `API_HOST` on your CALC instance to be
the combination of your **Frontend Host** and **Frontend Prefix**.
For example, given the earlier examples listed above, your
`API_HOST` setting on CALC would be `https://api.data.gov/gsa/calc/`.

Finally, as mentioned in the [Securing your API backend][] section of the
user manual, you will likely need to configure `WHITELISTED_IPS` on
your CALC instance to ensure that clients can't bypass rate limiting by
directly contacting your CALC instance.

[UPS]: https://docs.cloudfoundry.org/devguide/services/user-provided.html
[`README.md`]: https://github.com/18F/calc#readme
[API Umbrella]: https://apiumbrella.io/
[api.data.gov User Manual]: https://github.com/18F/api.data.gov/wiki/User-Manual:-Agencies
[Securing your API backend]: https://github.com/18F/api.data.gov/wiki/User-Manual:-Agencies#securing-your-api-backend
