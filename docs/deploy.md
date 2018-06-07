## Deploying to Cloud Foundry

**This section is only of interest to 18F team members.**

Download the Cloud Foundry CLI according to the [cloud.gov instructions][].
Make sure you are using at least version v6.17.1, otherwise pushing
multiple apps at once might not work.

[cloud.gov instructions]: https://docs.cloud.gov/getting-started/setup/

You will also need to install the [`autopilot`](https://github.com/contraband/autopilot)
plugin for Cloud Foundry, which is used for zero-downtime deploys.
You can install via
`cf install-plugin autopilot -f -r CF-Community`.

CALC is deployed to the GovCloud instance of cloud.gov. You will need to login
to via the GovCloud api of cloud.gov:
`cf login -a api.fr.cloud.gov --sso`

Then target the org and space you want to work with. For example, if you wanted to work with the dev space:
`cf target -o fas-calc -s dev`

Manifest files, which contain import deploy configuration settings, are located
in the [manifests](../manifests/) directory of this project.

Note that this project has two requirements files:
* `requirements.txt` for production dependencies
* `requirements-dev.txt` for development and testing dependencies

During local development and continuous integration testing,
`pip install -r requirements-dev.txt` is used, which installs both
development and production dependencies. During deployments, the Cloud
Foundry python buildpack uses only `requirements.txt` by default, so
only production dependencies will be installed.

### Cloud Foundry structure

- cloud.gov environment: `GovCloud`
- Organization: `fas-calc`
- Spaces: `dev`, `staging`, `prod`
- Apps:
  - `dev` space:
    - `calc-dev`
    - `calc-rqworker`
    - `calc-rqscheduler`
  - `staging` space:
    - `calc-staging`
    - `calc-rqworker`
    - `calc-rqscheduler`
  - `prod` space:
    - `calc-prod`
    - `calc-rqworker`
    - `calc-rqscheduler`
    - `calc-maintenance`
- Routes:
  - calc-dev.app.cloud.gov -> `dev` space, `calc-dev` app
  - calc-staging.app.cloud.gov -> `staging` space, `calc-staging` app
  - calc-prod.app.cloud.gov -> `prod` space, `calc-prod` app
  - calc.gsa.gov -> `prod` space, `calc-prod` app
    or the maintenance page app, `calc-maintenance`

### Services

#### Identity Provider Service

CALC uses an [Identity Provider Service][IPS] to register with cloud.gov's User Account and Authentication (UAA)
server (see [Auth](auth.md) for more details).

A service and associated service key are needed for each cloud.gov space.
As an example, for the `dev` space, the commands to create the service and get its keys are:

```sh
cf create-service cloud-gov-identity-provider oauth-client calc-dev-uaa-client
cf create-service-key calc-dev-uaa-client calc-dev-uaa-client-service-key -c '{"redirect_uri": ["https://calc-dev.app.cloud.gov"]}'
cf service-key calc-dev-uaa-client calc-dev-uaa-client-service-key
```

The `cf service-key` command above will output a username and password pair that corresponds to the `UAA_CLIENT_ID` and `UAA_CLIENT_SECRET`
environment variables that will be used when setting up CALC's User Provided Service, described in the next section.

See the [Identity Provider Service docs][IPS] for up-to-date information on its use.

#### User Provided Service (UPS)

For cloud.gov deployments, this project makes use of a [User Provided Service (UPS)][UPS] to get its configuration
variables, instead of using the local environment (except for [New Relic-related environment variables](#new-relic-environment-variables)).
You will need to create a UPS called `calc-env`, provide 'credentials' to it, and link it to the
application instance. This will need to be done for every Cloud Foundry `space`.

First, create a JSON file (e.g. `credentials-staging.json`) with all the configuration values specified as per the
[Environment variables](environment.md). **DO NOT COMMIT THIS FILE.**

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
cf bind-service <APP_INSTANCE> calc-env
cf restage <APP_INSTANCE>
```

You can update the user-provided service with the following commands:

```sh
cf uups calc-env -p credentials-staging.json
cf restage calc-dev
```

#### Database service

CALC uses PostgreSQL for its database.

```sh
cf create-service aws-rds <SERVICE_PLAN> calc-db
cf bind-service <APP_INSTANCE> calc-db
```

#### Redis service

CALC uses Redis along with [rq](http://python-rq.org/) for scheduling and processing
asynchronous tasks.

For production, use the `standard-ha` (high availability) plan. For non-production uses, use the `standard` plan.

```sh
cf create-service redis32 standard-ha calc-redis32
cf bind-service <APP_INSTANCE> calc-redis32
```

For more information on cloud.gov's Redis service, see its [docs](https://cloud.gov/docs/services/redis/).

### New Relic environment variables

Basic New Relic configuration is done in [newrelic.ini](../newrelic.ini), with
additional settings specified in each deployment environment's [manifest](../manifests/) file.

As described in [Environment variables](environment.md), you will need
to supply the `NEW_RELIC_LICENSE_KEY` as part of each deployment's
[User Provided Service](#user-provided-service-ups).

### Staging server

The staging server updates automatically when changes are merged into the
`develop` branch. Check out the `deploy` sections of
the [CircleCI config](../.circleci/config.yml) for details and settings.

Should you need to, you can push directly to calc-dev.app.cloud.gov with:

```sh
cf target -o fas-calc -s dev
cf push -f manifests/manifest-staging.yml
```

### Production servers

Production deploys are a somewhat manual process in that they are not done
from CI. However, just like in our CircleCI deployments to staging, we use the
Cloud Foundry [autopilot plugin](https://github.com/contraband/autopilot).

To deploy, first make sure you are targeting the prod space:

```sh
cf target -o fas-calc -s prod
```

Now, if you don't already have the autopilot plugin, you can install it by running:

```sh
cf install-plugin autopilot -f -r CF-Community
```

At the time of writing, we did not have enough memory allocated to do a `zero-downtime-push`
(which effectively doubles memory usage since it spins up another app instance)
without first decreasing the memory footprint. This can be accomplished by scaling
down the number of app instances:

```sh
cf scale -i 1 calc-prod
```

Then use the autopilot plugin's `zero-downtime-push` command to deploy:

```sh
cf zero-downtime-push calc-prod -f manifests/manifest-prod.yml
```

If a breaking database migration needs to be done, things get a little trickier because
the database service is actually shared between the two production apps. If the migration
breaks the current version of CALC, we'll need to have a (hopefully short) amount of downtime.

We have a very simple maintenance page application that uses the CloudFoundry staticfiles
buildpack. This app is in the [maintenance_page](../maintenance_page/) subdirectory.

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

### Logs

Logs in cloud.gov-deployed applications are generally viewable by running
`cf logs <APP_NAME> --recent`.

Note that the web application and the `rq` worker application have separate
logs, so you will need to look at each individually.

If more detailed log analysis is needed, Kibana can be used to generate
a variety of visualizations and dashboards. For more details, see the
[cloud.gov Logs documentation](https://cloud.gov/docs/apps/logs/).

### Initial superuser

After the initial setup of `calc-db` and a production app, you will need to
create a superuser account, after which you'll be able to login to the
Django admin panel to add additional user accounts. The easiest way to create
the initial superuser is to use `cf ssh` to get to the remote host
and run `python manage.py createsuperuser`. You'll need to do some environment
setup on the remote host, as described at [Cloud Foundry's SSH docs](https://docs.cloudfoundry.org/devguide/deploy-apps/ssh-apps.html#ssh-env):

```sh
export HOME=/home/vcap/app
export TMPDIR=/home/vcap/tmp
cd /home/vcap/app
source /home/vcap/app/.profile.d/python.sh
```

### Testing production deployments

Because reverse proxies like CloudFront can be misconfigured to prevent
CALC from working properly, we've built a test suite that can be used to
remotely test a production deployment of CALC. To use it, run:

```
py.test production_tests
```

By default, the suite tests against calc.gsa.gov. If you'd like to
test it against a different URL, you can do so with the `--origin`
command-line option.

[UPS]: https://docs.cloudfoundry.org/devguide/services/user-provided.html
[IPS]: https://cloud.gov/docs/services/cloud-gov-identity-provider/
[`README.md`]: https://github.com/18F/calc#readme
[api.data.gov User Manual]: https://github.com/18F/api.data.gov/wiki/User-Manual:-Agencies
[Securing your API backend]: https://github.com/18F/api.data.gov/wiki/User-Manual:-Agencies#securing-your-api-backend
