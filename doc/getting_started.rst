Getting started
---------------

This section will get you up and running with Psephology. It is assumed that you
have a working `docker <https://www.docker.com/>`_ installed. It's preferable to
have `docker-machine <https://docs.docker.com/machine/>`_ installed as well
because it's awesome.

Docker hub
``````````

Psephology can be got up and running without needing to clone the source
repository since there is an `image
<https://hub.docker.com/r/rjw57/psephology/>`_ on Docker hub which is built
automatically on each commit to master.

The image is configured to use the SQLite database internally and so should be
considered an "ephemeral" install in that the database state is not persisted.
In production, a further Dockerfile would be used which builds on this image and
adds configuration for a persistent database.

Since docker will automatically pull images not available locally, we can fetch
and run the Psephology server in one line:

.. code:: console

    $ docker run -it --rm --name psephology-server \
        -p 5000:5000 rjw57/psephology

Although the container is now running, trying to visit the site will result in
an error. This is because we've not yet migrated the database to the latest
version. Database migration is the process of updating the schema to match the
latest version. It's good practice to have the migration be under the control of
a separate command so that potentially database changing operations are
explicit.

The database migration takes one command. In a separate terminal,

.. code:: console

    $ docker exec psephology-server flask db upgrade

Now you should be able to navigate to http://localhost:5000/ and see the app in
all of its glory. If you're using ``docker-machine``, you'll need to use the
appropriate IP for the virtual machine:

.. code:: console

    $ xdg-open http://$(docker-machine ip):5000 # Linux-y machines
    $ open http://$(docker-machine ip):5000     # Mac OS X


Installation from source
````````````````````````

Firstly, clone the Psephology application from GitHub:

.. code:: console

    $ git clone https://github.com/rjw57/psephology
    $ cd psephology

Once can now build the Docker container directly from the repo:

.. code:: console

    $ docker build -t rjw57/psephology .

As part of the container build, the test suite is run to ensure that the current
version is runnable inside the container environment. Once the container is
built, you can run the server using ``docker run`` as outlined above.

Alternatively, you can opt for a local install via ``pip``. It is good practice
to setup a virtualenv first:

.. code:: console

    $ virtualenv -p $(which python3) venv
    $ . ./venv/bin/activate
    $ pip install -e .

Once installed, the test suite can be run via ``setup.py``:

.. code:: console

    $ python setup.py test

Code coverage can be calculated using the ``coverage`` utility:

.. code:: console

    $ pip install coverage
    $ coverage run setup.py test && coverage report

Migrate the initial database and start the server:

.. code:: console

    $ export PSEPHOLOGY_CONFIG=$PWD/config.py
    $ export FLASK_APP=psephology.autoapp
    $ export FLASK_DEBUG=1
    $ flask db upgrade
    $ flask run

When installed from source, the server is configured in "debug" mode with the
Flask debug toolbar inserted into the UI. You should be able to navigate to
http://localhost:5000/ and use the webapp.

Getting data in
```````````````

We can look around the site but at the moment there isn't much to see since
there's no data in the database. The Psephology repo comes with the results of
the General Election 2017 in the correct results format. You can use the
excellent `httpie <https://github.com/jakubroztocil/httpie>`_ tool to post the
results:

.. code:: console

    $ pip install httpie    # if you don't have it
    $ cat test-data/ge2017_results.txt | \
        http POST http://$(docker-machine ip):5000/api/import
    {
      "diagnostics": [], 
      "line_count": 650
    }

Note the ``diagnostics`` field which is returned. If we add some bad results
lines then human-readable errors are returned:

.. code:: console

    $ cat test-data/noisy_results.txt | \
        http POST http://$(docker-machine ip):5000/api/import
    {
      "diagnostics": [
        {
          "line": "Strangford, 507, X, 607, G", 
          "line_number": 1, 
          "message": "Party code \"X\" is unknown"
        }, 
        {
          "line": "", 
          "line_number": 5, 
          "message": "Constituency name cannot be empty"
        }, 
        {
          "line": "Oxford East, 11834, C, 35118, L, 4904, LD, 1785, G, 10, LD", 
          "line_number": 6, 
          "message": "Multiple results for one party"
        }
      ], 
      "line_count": 7
    }

We can use the API to get a table listing how many seats each party currently
has:

.. code:: console

    $ http http://$(docker-machine ip):5000/api/party_totals 
    {
      "party_totals": {
        "C": {
          "constituency_count": 321, 
          "name": "Conservative Party"
        }, 
        "G": {
          "constituency_count": 8, 
          "name": "Green Party"
        }, 
        "L": {
          "constituency_count": 263, 
          "name": "Labour Party"
        }, 
        "LD": {
          "constituency_count": 13, 
          "name": "Liberal Democrats"
        }, 
        "SNP": {
          "constituency_count": 35, 
          "name": "SNP"
        }
      }
    }

Similarly we can retrieve the winners of each constituency via the API. Results
are returned for each constituency even when there is currently no winner. (For
example if a blank results line has been given.)

.. code:: console

    $ http http://$(docker-machine ip):5000/api/constituencies
    {
      "constituencies": [
        {
          "maximum_votes": 22662, 
          "name": "Aberavon", 
          "party": {
            "id": "L", 
            "name": "Labour Party"
          }, 
          "share_percentage": 74.28459042187039, 
          "total_votes": 30507
        }, 

        // ....

        {
          "maximum_votes": null, 
          "name": "Belfast West", 
          "party": null, 
          "share_percentage": null, 
          "total_votes": null
        },

        // ....

        {
          "maximum_votes": 34594, 
          "name": "York Central", 
          "party": {
            "id": "L", 
            "name": "Labour Party"
          }, 
          "share_percentage": 65.16350210970464, 
          "total_votes": 53088
        }, 
        {
          "maximum_votes": 29356, 
          "name": "York Outer", 
          "party": {
            "id": "C", 
            "name": "Conservative Party"
          }, 
          "share_percentage": 51.118811708778104, 
          "total_votes": 57427
        }
      ]
    }

It is also possible to update a constituency result via the API. For example,
let's allow the Liberal Democrats to win Cambridge:

.. code:: console

    $ echo Cambridge, 10, C, 10, L, 1000, LD |
        http POST http://$(docker-machine ip):5000/api/import
    {
      "diagnostics": [], 
      "line_count": 1
    }

Looking at the party totals, we see that Labour have lost one seat and the
Liberal Democrats have gained one:

.. code:: console

    $ http http://$(docker-machine ip):5000/api/party_totals 
    {
      "party_totals": {
        "C": {
          "constituency_count": 321, 
          "name": "Conservative Party"
        }, 
        "G": {
          "constituency_count": 8, 
          "name": "Green Party"
        }, 
        "L": {
          "constituency_count": 262, 
          "name": "Labour Party"
        }, 
        "LD": {
          "constituency_count": 14, 
          "name": "Liberal Democrats"
        }, 
        "SNP": {
          "constituency_count": 35, 
          "name": "SNP"
        }
      }
    }

Building the documentation
``````````````````````````

The documentation is built with the ``sphix`` tool and has additional
requirements. You can install the requirements and build the documentation via:

.. code:: console

    $ pip install -r doc/requirements.txt
    $ make -C doc singlehtml
    $ xdg-open doc/_build/singlehtml/index.html     # Linux-y
    $ open doc/_build/singlehtml/index.html         # OS X

