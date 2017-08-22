# Psephology - the study of elections

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

## Running tests

```console
$ python setup.py test
```

