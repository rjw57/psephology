# Psephology - the study of elections

[![Build
Status](https://travis-ci.org/rjw57/psephology.svg?branch=master)](https://travis-ci.org/rjw57/psephology)
[![Coverage
Status](https://coveralls.io/repos/github/rjw57/psephology/badge.svg?branch=master)](https://coveralls.io/github/rjw57/psephology?branch=master)
[![Documentation
Status](https://readthedocs.org/projects/psephology/badge/?version=latest)](http://psephology.readthedocs.io/en/latest/?badge=latest)
[![Docker Build
Statu](https://img.shields.io/docker/build/rjw57/psephology.svg)](https://hub.docker.com/r/rjw57/psephology/)

Psephology is an experimental webapp for recording election results. For more
information take a look at the
[documentation](http://psephology.readthedocs.io/en/latest/).

## Getting started

The [documentation](http://psephology.readthedocs.io/en/latest/) includes a
simple getting started guide which covers building a Docker container to host
the application. The information below is of more use if you are working on the
project and want to run a local development server.

### Short, short version

```console
$ docker pull rjw57/psephology
$ docker run -it --rm --name psephology-server -p 5000:5000 rjw57/psephology
```

In another terminal:

```console
$ docker exec psephology-server flask db upgrade
```

Now visit http://localhost:5000/ or, if you're using
[docker-machine](https://docs.docker.com/machine/):

```console
$ xdg-open http://$(docker-machine ip):5000/    # Linux-y
$ open http://$(docker-machine ip):5000/        # OS X
```

### Local server

You need to run ``flask db upgrade`` before running the server:

```console
$ export PSEPHOLOGY_CONFIG=$PWD/config.py
$ export FLASK_APP=psephology.autoapp
$ export FLASK_DEBUG=1
$ flask db upgrade
$ flask psephology importlayouts layouts.yaml
$ flask run
```

The ``config.py`` file should look something like the following:

```python
from psephology.config.dev import *

# Any custom config here
```

## New results

New results can be imported via the ``importresults`` CLI command. For example:

```console
$ flask psephology importresults test-data/ge2017_results.txt
```

## Running tests

Tests are run via the ``setup.py`` script. When the Docker container is built,
tests are run within it.

```console
$ python setup.py test
```
