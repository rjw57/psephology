"""
Automatic app creation
======================

The :py:module:`.autoapp` module may be imported to automatically create an
application from the configuration specified in the ``PSEPHOLOGY_CONFIG``
environment variable. This is useful, for example, when using the `gunicorn`_
web server where one can launch the application via:

.. code:: console

    $ gunicorn psephology.autoapp:app

_`gunicorn`: http://gunicorn.org/

"""

import os
from . import create_app

app = create_app(os.environ['PSEPHOLOGY_CONFIG'])
