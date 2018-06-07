## Using Docker

A Docker setup potentially makes development and deployment easier.

To use it, install [Docker][] and [Docker Compose][] and read the
[18F Docker guide][] if you haven't already.

Then run:

```sh
cp .env.sample .env
ln -sf docker-compose.local.yml docker-compose.override.yml
./docker-update.sh
```

You can optionally load some data into your dockerized database with:

```sh
docker-compose run app python manage.py load_api_data --end-page=5
```

Once the above commands are successful, run:

```sh
docker-compose up
```

This will start up all required servers in containers and output their
log information to stdout. You should be able to visit http://localhost:8000/
directly to access the site.

### Changing the exposed port

If you don't want to serve your app on port 8000, you can change
the value of `DOCKER_EXPOSED_PORT` in your `.env` file.

### Accessing the app container

You'll likely want to run `manage.py` or `py.test` to do other things at
some point. To do this, it's probably easiest to run:

```sh
docker-compose run app bash
```

This will run an interactive bash session inside the main app container.
In this container, the `/calc` directory is mapped to the root of
the repository on your host; you can run `manage.py` or `py.test` from there.

Note that if you don't have Django installed on your host system, you
can just run `python manage.py` directly from outside the container--the
`manage.py` script has been modified to run itself in a Docker container
if it detects that Django isn't installed.

### Updating the containers

Whenever you update your repository via e.g. `git pull` or
`git checkout`, you should update your containers by running
`./docker-update.sh`.

### Custom dependencies

Feel free to install custom dependencies, e.g. your favorite
debugging library, in your container via
`docker-compose run app pip install` or
`docker-compose run app yarn add`. Everything should work
as expected.

### Debugging Python

CALC's `requirements-dev.txt` file will install [`ipdb`][].

To drop into an interactive debugging section, add `import ipdb;
ipdb.set_trace()` on the line above the point you want to start your debugging
session. Then run Docker using the `service-ports` option: `docker-compose run
--service-ports app`. Your interactive debugging session should start in your
terminal when you reload the page.

Here's a [handy list of `ipdb` commands][ipdb_intro].

[`ipdb`]: https://pypi.python.org/pypi/ipdb
[ipdb_intro]: https://www.safaribooksonline.com/blog/2014/11/18/intro-python-debugger/

### Deploying to cloud environments

The Docker setup can also be used to deploy to cloud environments.

To do this, you'll first need to
[configure Docker Machine for the cloud][docker-machine-cloud],
which involves provisioning a host on a cloud provider and setting up
your local environment to make Docker's command-line tools use that
host. For example, to do this on Amazon EC2, you might use:

```
docker-machine create aws16 --driver=amazonec2 --amazonec2-instance-type=t2.large
```

Docker Machine's cloud drivers intentionally don't support
folder sharing, which means that you can't just edit a file on
your local system and see the changes instantly on the remote host.
Instead, your app's source code is part of the container image. To
facilitate this, you'll need to create a new Dockerfile that augments
your existing one:

```
cat Dockerfile Dockerfile.cloud-extras > Dockerfile.cloud
```

Also, unlike local development, cloud deploys don't support an
`.env` file. So you'll want to create a custom
`docker-compose.override.yml` file that defines the app's
environment variables, and also points to the alternate Dockerfile:

```
cp docker-compose.cloud.yml docker-compose.override.yml
```

You can edit this file to add or change environment variables as needed.

You'll also want to tell Docker Compose what port to listen on,
which can be done in the terminal by running
`export DOCKER_EXPOSED_PORT=8000`.

At this point, you can use Docker's command-line tools and CALC's
Docker-related scripts, and your actions will take effect on the remote
host instead of your local machine.

So, you should first run `./docker-update.sh` to set everything up,
followed by `docker-compose up`. Now you should have a server
running in the cloud!

**Note:** A script, [create-aws-instance.sh](../create-aws-instance.sh),
actually automates all of this for you, but it's coupled to Amazon
Web Services (AWS). You're welcome to use it directly or edit it to
your own needs. Run it without any arguments for help.

**Note:** As mentioned earlier, your app's source code is part of
the container image. This means that every time you make a source code
change, you will need to re-run `./docker-update.sh`.

[18F Docker guide]: https://pages.18f.gov/dev-environment-standardization/virtualization/docker/
[Docker]: https://www.docker.com/
[Docker Compose]: https://docs.docker.com/compose/
[docker-machine-cloud]: https://docs.docker.com/machine/get-started-cloud/
