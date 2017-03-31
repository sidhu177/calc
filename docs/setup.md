## Setup

Setting up CALC locally without Docker is possible, but it requires
quite a few prerequisites. If the following instructions seem daunting,
you may want to check out our alternative [Docker instructions](docker.md).

### Prerequisites

You'll need the following tools and services installed to run CALC
locally:

* [Python 3.6.0](https://www.python.org/)
* [Node 6.0](https://nodejs.org/)
* [yarn](https://yarnpkg.com)
  * Install globally via `npm install -g yarn`
* [Postgres 9.5](https://www.postgresql.org/)
  * It's easiest to have a local instance of it running on its default
    port, as this requires no extra configuration on the CALC side.
* [Redis](https://redis.io/)
  * It's easiest to have a local instance of it running on its default
    port, as this requires no extra configuration on the CALC side.
  * For guidance on installing Redis, see
    [Installing Redis on Mac OSX][redis-osx] or
    [Installing Redis on Ubuntu][redis-ubuntu].

### Configuration

CALC is a [Django] project. You can configure everything by running:

```sh
cp .env.sample .env
```

Edit the `.env` file to your tastes. If all your services are on their
default ports, you shouldn't need to change much here; if not, see
[Environment variables](environment.md) for details on
configuration.

### Creating the database

Assuming you haven't changed the database mentioned in the
your `.env` file's `DATABASE_URL` value from its default value,
you can create the Postgres database by running:

```sh
createdb hourglass
```

### Running the update script

Now run:

```sh
./update.sh
```

This script will install/update all Python and Node dependencies,
as well as apply any necessary database migrations.

You'll also want to run this script whenever you update your repository
via commands like `git pull` or `git checkout`.

### Loading data (optional)

After that, you can optionally load all of the data by running:

```sh
./manage.py load_data
./manage.py load_s70
```

### Starting the development server

Now you can start the development server:

```sh
./manage.py runserver
```

Don't visit it just yet, though--first you'll need to start the static
asset build pipeline.

### Starting the static asset generator

In another terminal, you will also need to run `gulp` to watch and rebuild
static assets:

```sh
npm run gulp
```

### Starting the task runner

Also, in yet another terminal, you will want to run
the following to process all the tasks in the task queue:

```sh
python manage.py rqworker
```

### Starting the task scheduler (optional)

You can also start CALC's task scheduler in a separate terminal,
though it's not required:

```sh
IS_RQ_SCHEDULER=yup python manage.py rqscheduler
```

### Visiting the development server

Now you're ready to visit your local development site! Load
http://localhost:8000/ in your browser.

[redis-ubuntu]: https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-redis-on-ubuntu-16-04

[redis-osx]: https://medium.com/@petehouston/install-and-config-redis-on-mac-os-x-via-homebrew-eb8df9a4f298#.fa2s6i1my

[Django]: https://www.djangoproject.com/
