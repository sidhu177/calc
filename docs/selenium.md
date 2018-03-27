## Browser tests via Selenium

### Environment variables

#### Required variables

To run CALC's browser-based tests via Selenium/WebDriver in a real-world
(i.e., non-PhantomJS) browser, you'll need to define the following
environment variables, unless otherwise noted:

* `DJANGO_LIVE_TEST_SERVER_ADDRESS` is the IP and port that CALC
  will bind itself to from the perspective of the machine (or
  Docker container) running the tests, e.g. `0.0.0.0:8000`.

* `WD_HUB_URL` is the URL at which the [Selenium hub][] server resides
  from the perspective of the machine (or Docker container) running
  the tests, e.g. `http://localhost:4444/wd/hub`.

* `WD_TESTING_URL` is the URL from which the automated browser will be able
  to access CALC, e.g. `http://localhost:8000`. (This will literally be
  the base URL that appears in the automated browser's address bar.)

* `WD_TESTING_BROWSER` is the browser used to perform the automated tests.
  Examples include `chrome`, `firefox`, `internet explorer`, `android`,
  `chrome`, `iPhone`, `iPad`, `opera`, and `safari`.

#### Optional variables

The following can also be optionally defined:

* `WD_TESTING_PLATFORM` is the operating system the browser should
  be running on.

* `WD_TESTING_BROWSER_VERSION` is the browser version to test with.

* `WD_SOCKET_TIMEOUT` specifies the default socket timeout to use for
  requests before giving up, in seconds.

### Example: Docker on OS X

If you're using Docker, configuration may not be straightforward due
to the fact that CALC is running in its own Docker container with its
own network.

The hardest part of this setup is figuring out an IP address that
docker containers can reach your machine through. 

One way to do this is by using the IP address of your
machine on your LAN; on OS X, for instance, you should be able to
use the output of the following command:

```
ipconfig getifaddr en0
```

The following instructions assume this command output `192.168.1.5`;
your situation will likely differ, so substitute your own machine's IP
as needed.

Below is an example configuration for running tests in a
[Selenium Docker image][]--specifically, a headless Chrome browser. They
assume that you're using a native version of Docker that exposes CALC
through the default `DOCKER_EXPOSED_PORT` of `8000`.

1. In a separate terminal, run:

   ```
   docker run -it --rm -p 4444:4444 -v /dev/shm:/dev/shm selenium/standalone-chrome:2.53.1
   ```

   This will start up the Selenium hub server connected to a headless
   Chrome in a docker container.

2. **This step is optional.** To make sure your Selenium server is
   reachable from CALC, you may want to run the following:

   ```
   docker-compose run app curl -I http://192.168.1.5:4444/wd/hub
   ```

   This command should result in a 302 if it's able to connect to your
   Selenium server.

3. Set the following environment variables in your `.env` file:

   ```
   DJANGO_LIVE_TEST_SERVER_ADDRESS=0.0.0.0:8000
   WD_TESTING_URL=http://192.168.1.5:8000
   WD_HUB_URL=http://192.168.1.5:4444/wd/hub
   WD_TESTING_BROWSER=chrome
   ```

4. If you're running `docker-compose up` in a separate terminal,
   shut it down now, because the test server is going to be exposing
   itself on the same port as that development server.

5. Run the following:

   ```
   docker-compose run --service-ports app python manage.py test frontend
   ```

   If you need to run this multiple times but aren't changing any
   front end code between runs, set `SKIP_STATIC_ASSET_BUILDING=yup` in
   your `.env` to make things run faster.


#### Running the tests on your machine's Chrome browser

One disadvantage of running Chrome headless is that you can't easily
see what's going on. You can get around this by running the Selenium
tests using your own machine's Chrome browser, but it takes some
extra configuration:

1. Download [Selenium Standalone Server][].  To run it, you will need to
   install Java too. Start it up with `java -jar` followed by the
   name of the `.jar` file you downloaded.

   Alternatively, if you use Homebrew, you should be able to install
   it via `brew install selenium-standalone-server`.

2. Download [ChromeDriver][], decompress its executable and put it in the
   same directory as Selenium Standalone Server.

   Alternatively, if you use Homebrew, `brew install chromedriver` should
   work.

Now, follow the earlier example's instructions from step (2) onward.

[Selenium hub]: https://seleniumhq.github.io/docs/grid.html#what_is_a_hub_and_node
[Selenium Standalone Server]: http://www.seleniumhq.org/download/
[ChromeDriver]: https://sites.google.com/a/chromium.org/chromedriver/
[Selenium Docker image]: https://github.com/SeleniumHQ/docker-selenium
