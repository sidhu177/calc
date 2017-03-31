## Environment variables

Unlike traditional Django settings, we use environment variables
for configuration to be compliant with [twelve-factor][] apps.

You can define environment variables using your environment, or
(if you're developing locally) an `.env` file in the root directory
of the repository. For more information on configuring
environment variables on cloud.gov, see
[Deploying to Cloud Foundry](deploy.md).

**Note:** When an environment variable is described as representing a
boolean value, if the variable exists with *any* value (even the empty
string), the boolean is true; otherwise, it's false.

* `DEBUG` is a boolean value that indicates whether debugging is enabled
  (this should always be false in production).

* `DEBUG_HTTPS` is a boolean value that indicates whether the
  site should consider itself to be served over HTTPS while
  debugging is enabled. This can be useful if you want to develop
  with SSL enabled.

* `HIDE_DEBUG_UI` is a boolean value that indicates whether to hide
  various development and debugging affordances in the UI, such as the
  [Django Debug Toolbar][]. This can be useful when demoing or user testing
  a debug build.

* `SECRET_KEY` is a large random value corresponding to Django's
  [`SECRET_KEY`][] setting. It is automatically set to a known, insecure
  value when `DEBUG` is true.

* `DATABASE_URL` is the URL for the database, as per the
  [DJ-Database-URL schema][]. Note that the protocol *must* be
  `postgres:`.

* `EMAIL_URL` is the URL for the service to use when sending
  email, as per the [dj-email-url schema][]. When `DEBUG` is true,
  this defaults to `console:`. If it is set to `dummy:` then no emails will
  be sent and messages about email notifications will not be shown to users.
  The setting can easily be manually tested via the `manage.py sendtestemail`
  command.

* `DEFAULT_FROM_EMAIL` is the email from-address to use in all system
  generated emails to users. It corresponds to Django's [`DEFAULT_FROM_EMAIL`][]
  setting. It defaults to `noreply@localhost` when `DEBUG=True`.

* `SERVER_EMAIL` is the email from-address to use in all system generated
  emails to managers and admins. It corresponds to Django's [`SERVER_EMAIL`][]
  setting. It defaults to `system@localhost` when `DEBUG=True`.

* `HELP_EMAIL` is the email  used as the reply-to address in system
  generated emails to users. It is also the email address used in the site
  footer and for other contact purposes. It should refer to an inbox that is
  monitored. If not set, it will use the same value as `DEFAULT_FROM_EMAIL`.

* `REDIS_URL` is the URL for redis, which is used by the task queue.
  When `DEBUG` is true, it defaults to `redis://localhost:6379/0`.

* `REDIS_TEST_URL` is the redis URL to use when running tests.
  When `DEBUG` is true *and* `REDIS_URL` isn't defined, it defaults to
  `redis://localhost:6379/1`.

* `ENABLE_SEO_INDEXING` is a boolean value that indicates whether to
  indicate to search engines that they can index the site.

* `FORCE_DISABLE_SECURE_SSL_REDIRECT` is a boolean value that indicates
  whether to disable redirection from http to https. Because such
  redirection is enabled by default when `DEBUG` is false, this option
  can be useful when you want to simulate *almost* everything about a
  production environment without having to setup SSL.

* `UAA_CLIENT_ID` is your cloud.gov/Cloud Foundry UAA client ID. It
  defaults to `calc-dev`.

* `UAA_CLIENT_SECRET` is your cloud.gov/Cloud Foundry UAA client secret.
  If this is undefined and `DEBUG` is true, then a built-in Fake UAA Provider
  will be used to "simulate" cloud.gov login.

* `WHITELISTED_IPS` is a comma-separated string of IP addresses that specifies
  IPs that the REST API will accept requests from. Any IPs not in the list
  attempting to access the API will receive a 403 Forbidden response.
  Example: `127.0.0.1,192.168.1.1`.

* `API_HOST` is the relative or absolute URL used to access the
  API hosted by CALC. It defaults to `/api/` but may need to be changed
  if the API has a proxy in front of it, as it likely will be if deployed
  on government infrastructure. For more information, see
  the [API documentation](api.md).

* `SECURITY_HEADERS_ON_ERROR_ONLY` is a boolean value that indicates whether
  security-related response headers (such as `X-XSS-Protection`)
  should only be added on error (status code >= 400) responses. This setting
  will likely only be used for cloud.gov deployments, where the built-in proxy
  sets those security headers on 200 responses but not on others.

* `GA_TRACKING_ID` is the tracking ID (e.g. `'UA-12345678-12'`)
  for the associated Google Analytics account.
  It will default to the empty string if not found in the environment.

* `NON_PROD_INSTANCE_NAME` is an optional instance name that when specified
  will cause a banner to be shown at the top of every page to let users know
  that they are viewing a non-production instance of CALC. This value
  can contain HTML, so it's possible to e.g. wrap the value in a hyperlink.

* `NEW_RELIC_LICENSE_KEY` is the private New Relic license key for this project.
  If it is present, then the WSGI app will be wrapped with the  New Relic agent.

* `TEST_WITH_ROBOBROWSER` is a boolean that indicates whether to run
  some integration tests using [RoboBrowser][] instead of Selenium/WebDriver.
  Running tests with RoboBrowser can be much faster and less error-prone
  than via Selenium, but it also means that the tests are less end-to-end.

* `SLACKBOT_WEBHOOK_URL` is the URL of a [Slack incoming webhook][] that
  will be sent messages whenever certain kinds of
  [events](../slackbot/signals.py) occur in the app.

* `ESLINT_CHILL_OUT` is a boolean; if true, it will change the behavior
  of gulp's watch mode such that it doesn't run `eslint` every time a
  file changes.

[RoboBrowser]: http://robobrowser.readthedocs.io/
[`SECRET_KEY`]: https://docs.djangoproject.com/en/1.8/ref/settings/#secret-key
[`DEFAULT_FROM_EMAIL`]: https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-DEFAULT_FROM_EMAIL
[`SERVER_EMAIL`]: https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-SERVER_EMAIL
[Django Debug Toolbar]: https://github.com/jazzband/django-debug-toolbar/
[DJ-Database-URL schema]: https://github.com/kennethreitz/dj-database-url#url-schema
[dj-email-url schema]: https://github.com/migonzalvar/dj-email-url#supported-backends
[twelve-factor]: http://12factor.net/
[Slack incoming webhook]: https://api.slack.com/incoming-webhooks
