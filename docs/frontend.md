# Front end

In general, front end code is in the [frontend](../frontend/) directory.

This guide is about the nuts-and-bolts of developing front end code; for
details on how to use or style individual components, see the
[style guide][].

## The static asset generator

If you haven't already, make sure you've followed the
[setup guide](setup.md); it explains how to get the gulp-based
static asset generator up and running. It will watch for changes to
front end code and re-build bundles as needed.

All the static assets (SASS for CSS and ES6 JavaScript) are
located in the [frontend/source/](../frontend/source/) directory. Outputs
from the static asset generator are placed in
`frontend/static/frontend/built/`.

Examine [gulpfile.js](../gulpfile.js) for details about the generator's
pipeline.

If you just want to build the assets once without watching for changes, run:

```sh
yarn gulp build
```

## Developing the front end

Different parts of CALC are constructed in different ways, so
developing the front end depends on which part you want to change.

We use [yarn][] to manage our node dependencies and run node tasks.
`yarn`, in addition to being faster than using `npm install`, has the
benefit of locking dependency versions via a `yarn.lock` file.
Read the [yarn workflow docs][] if you are not familiar with how to use it.

### Data explorer

The data explorer is a [React][]-based app that uses [Redux][] for
data flow and state management. It's located in
[frontend/source/js/data-explorer](../frontend/source/js/data-explorer/).

The explorer's test suite uses [Jest][], and the tests are located in
[frontend/source/js/data-explorer/tests](../frontend/source/js/data-explorer/tests/).

To run all the tests, run:

```
yarn test
```

You can also run the tests in a continuous "watch" mode, which re-runs
tests as you change your code:

```
yarn test:watch
```

Finally, you can also run `jest` directly. If you're using Docker,
this can be done via `docker-compose run app jest`; otherwise you can
use `yarn test`, followed by any
[Jest CLI options](https://facebook.github.io/jest/docs/cli.html).

### Data capture

Data capture largely consists of Django templates combined with
HTML5 Custom Elements to provide a progressively-enhanced experience.

The source code is located in
[frontend/source/js/data-capture](../frontend/source/js/data-capture/).

Tests are [QUnit][]-based and are located in
[frontend/source/js/tests](../frontend/source/js/tests/).

To run the QUnit tests, visit
[/tests/](https://calc-dev.app.cloud.gov/tests/) on your local
development instance.

### Administrative UI

We skin the Django administrative UI to look like part of the CALC
site; its templates are located in
[hourglass/templates/admin](../hourglass/templates/admin).

### Other components

Other parts of CALC are usually stored in either Django templates
or somewhere under the [frontend/source/](../frontend/source/)
hierarchy.

When in doubt, see the [style guide][]!

[QUnit]: https://qunitjs.com/
[React]: https://facebook.github.io/react/
[Redux]: http://redux.js.org/
[Jest]: https://facebook.github.io/jest/
[style guide]: https://calc-dev.app.cloud.gov/styleguide/
[yarn]: https://yarnpkg.com/
[yarn workflow docs]: https://yarnpkg.com/en/docs/yarn-workflow
