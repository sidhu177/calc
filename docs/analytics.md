## Analytics

### Browser

#### Google Analytics

CALC supports two kinds of integration with Google Analytics (GA):

1. The [Digital Analytics Program (DAP)][DAP] is a government-wide
   GA 360 Suite account.

2. Any other GA account, specified via the optional
   `GA_TRACKING_ID` environment variable.

For the most part, the same analytics metrics are sent to both
GA accounts.

Most of the JavaScript logic for Google Analytics integration
is in [ga.js](../frontend/source/js/common/ga.js), and
snippets included in HTML templates are in
[data_explorer/templates/analytics/](../data_explorer/templates/analytics/).
Please see these files for further documentation on how to track custom
events, virtual pageviews, and more.

#### New Relic

If the `NEW_RELIC_LICENSE_KEY` environment variable has been set
and the associated New Relic account has [New Relic Browser][]
enabled, the New Relic Python agent will automatically
inject JavaScript analytics script tags into CALC pages.

[New Relic Browser]: https://docs.newrelic.com/docs/browser/new-relic-browser/getting-started/introduction-new-relic-browser

### Server

When deploying via Cloud Foundry, Kibana
can be used to obtain server-side analytics.

For more details, see the [Deploying to Cloud Foundry](deploy.md)
documentation.

[DAP]: https://github.com/digital-analytics-program/gov-wide-code
