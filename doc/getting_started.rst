Getting started
---------------

Installation
````````````

This section will get you up and running with Psephology. It is assumed that you
have a working `docker <https://www.docker.com/>`_ installed. It's preferable to
have `docker-machine <https://docs.docker.com/machine/>`_ installed as well
because it's awesome.

Firstly, clone the Psephology application from GitHub:

.. code:: console

    $ git clone https://github.com/rjw57/psephology
    $ cd psephology

You could perform a standard ``pip install .`` to install the application but
we're going to pull the Docker container `image
<https://hub.docker.com/r/rjw57/psephology/>`_ from Docker hub. Should you need
to actually build the container, you can do so via:

.. code:: console

    $ docker build -t rjw57/psephology .

As part of the container build, the test suite is run to ensure that the current
version is runnable inside the container environment. Once the container is
built, you can run the server via ``docker run``:

.. code:: console

    $ docker run -it --rm --name psephology-server \
        -p 5000:5000 rjw57/psephology

Although the container is now running, trying to visit the site will result in
an error. This is because we've not yet migrated the datbase to the latest
version. In a separate terminal, run the database migration:

.. code:: console

    $ docker exec psephology-server flask db upgrade

Now you should be able to navigate to http://localhost:5000/ and see the app in
all of its glory. If you're using docker-machine, you'll need to use the
appropriate IP for the virtual machine:

.. code:: console

    $ xdg-open http://$(docker-machine ip):5000 # Linux-y machines
    $ open http://$(docker-machine ip):5000     # Mac OS X

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
Liberal Democrats have gained on:

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

