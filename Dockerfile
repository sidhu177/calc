FROM python:3.6.4

ENV PHANTOMJS_VERSION 1.9.7

# https://hub.docker.com/r/cmfatih/phantomjs/~/dockerfile/
RUN \
  mkdir -p /srv/var && \
  wget -q --no-check-certificate -O /tmp/phantomjs-$PHANTOMJS_VERSION-linux-x86_64.tar.bz2 https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-$PHANTOMJS_VERSION-linux-x86_64.tar.bz2 && \
  tar -xjf /tmp/phantomjs-$PHANTOMJS_VERSION-linux-x86_64.tar.bz2 -C /tmp && \
  rm -f /tmp/phantomjs-$PHANTOMJS_VERSION-linux-x86_64.tar.bz2 && \
  mv /tmp/phantomjs-$PHANTOMJS_VERSION-linux-x86_64/ /srv/var/phantomjs && \
  ln -s /srv/var/phantomjs/bin/phantomjs /usr/bin/phantomjs

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -

# Note that we want postgresql-client so 'manage.py dbshell' works.
RUN apt-get update && \
  apt-get install -y nodejs postgresql-client

RUN pip install virtualenv

WORKDIR /calc

RUN npm install -g yarn

ENV PATH /calc/node_modules/.bin:$PATH
ENV DDM_IS_RUNNING_IN_DOCKER yup

ENTRYPOINT ["python", "/calc/docker_django_management.py"]
