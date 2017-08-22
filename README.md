# Psephology - the study of elections

[![Build
Status](https://travis-ci.org/rjw57/psephology.svg?branch=master)](https://travis-ci.org/rjw57/psephology)
[![Coverage
Status](https://coveralls.io/repos/github/rjw57/psephology/badge.svg?branch=master)](https://coveralls.io/github/rjw57/psephology?branch=master)

## Development server

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

Tests are run via the ``setup.py`` script.

```console
$ python setup.py test
```

## Running via Docker

**Note:** these instructions assume [Docker
machine](https://docs.docker.com/machine/) is in use.

```console
$ docker build -t psephology .
$ docker run -it --rm --name psephology-server -p 5000:5000 psephology
$ docker exec psephology-server flask db upgrade
$ xdg-open http://$(docker-machine ip):5000
```
