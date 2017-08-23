Command line
------------

The Psephology application has a command-line interface which can be run via the
``flask`` tool. Perhaps the most useful command is ``flask run`` which will
launch a server hosting the application.

Database migration
``````````````````

Psephology uses Flask-Migrate and alembic to manage the database migrations. On
first run or when upgrading the software, remember to run ``flask db upgrade``
to migrate the database to the newest version.

Importing results
`````````````````

Results may be imported from the command line via ``flask psephology
importresults``. See ``flask psephology importresults --help`` for more
information.


