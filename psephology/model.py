"""
The :py:mod:`.model` module defines the basic data model used by Psephology
along with some utility functions which can be used to mutate it. The
:py:mod:`.query` module contains some potted queries for this data model which
provide useful summaries.

None of the functions in :py:mod:`.model` will run ``session.commit()``. If you
mutate the database inside a UI/API implementation, you'll need to remember to
commit the result. This is to guard against partial updates to the DB is a
UI/API method fails.

"""

import datetime
from sqlite3 import Connection as SQLite3Connection

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event as sqlalchemy_event, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import DEFAULT_NAMING_CONVENTION

from psephology.io import parse_result_line

# Create the shared database and migration singletons.
db = SQLAlchemy(
    metadata=MetaData(naming_convention=DEFAULT_NAMING_CONVENTION)
)
migrate = Migrate()

class Party(db.Model):
    """A political party. Each party is primarily keyed by its abbreviation. In
    addition, the name of a political party should be unique.

    .. py:attribute:: id

        String primary key. This is the party "code" such as "C" or "LD".

    .. py:attribute:: name

        Human-readable "long" name for the party.

    .. py:attribute:: votings

        Sequence of :py:class:`.Voting` instances associated with this party.

    """
    __tablename__ = 'parties'

    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, unique=True)

    votings = relationship('Voting', back_populates='party')

class Constituency(db.Model):
    """A constituency. Essentially this is a mapping between a numeric id and a
    human-friendly name.

    .. py:attribute:: id

        Integer primary key.

    .. py:attribute:: name

        Human-readable name. Must be unique.

    .. py:attribute:: votings

        Sequence of :py:class:`.Voting` instances associated with this
        constituency.

    """
    __tablename__ = 'constituencies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False)

    votings = relationship('Voting', back_populates='constituency')

class Voting(db.Model):
    """A record of a number of votes cast for a particular party within a
    constituency.

    .. py:attribute:: id

        Integer primary key.

    .. py:attribute:: count

        Number of votes cast.

    .. py:attribute:: constituency_id

        Integer primary key id of associated constituency.

    .. py:attribute:: constituency

        :py:class:`.Constituency` instance for associated constituency.

    .. py:attribute:: party_id

        String primary key id of associated party.

    .. py:attribute:: party

        :py:class:`.Party` instance for associated party.

    """
    __tablename__ = 'votings'

    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, nullable=False)
    constituency_id = db.Column(db.Integer,
        db.ForeignKey('constituencies.id', ondelete='CASCADE'),
        nullable=False)
    party_id = db.Column(db.Text,
        db.ForeignKey('parties.id', ondelete='CASCADE'),
        nullable=False)

    constituency = relationship('Constituency',
        back_populates='votings')
    party = relationship('Party',
        back_populates='votings')

class LogEntry(db.Model):
    """A record of some log-worthy text.

    .. py:attribute:: id

        Integer primary key.

    .. py:attribute:: created_at

        Date and time at which this entry was created in UTC. When creating an
        instance, this defaults to the current date and time.

    .. py:attribute:: message

        Textual content of log.

    """
    __tablename__ = 'log_entries'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False,
            default=datetime.datetime.utcnow, index=True)
    message = db.Column(db.Text)

def log(message):
    """Convenience function to log a message to the database."""
    db.session.add(LogEntry(message=message))

def _query_valid_party_codes(session=None):
    """Return a set of valid party codes."""
    session = session if session is not None else db.session
    return set(p.id for p in Party.query)

def add_constituency_result_line(line, valid_codes=None, session=None):
    """Add in a result from a constituency. Any previous result is removed. If
    there is an error, ValueError is raised with an informative message.

    Session is the database session to use. If None, the global db.session is
    used.

    If valid_codes is non-None, it is a set containing the party codes which are
    allowed in this database. If None, this set is queried from the database.

    The session is not commit()-ed.

    """
    session = session if session is not None else db.session
    valid_codes = (
        valid_codes if valid_codes is not None else
        _query_valid_party_codes(session)
    )

    cn, results = parse_result_line(line)

    # Check constituency name is non-empty
    if cn == '':
        raise ValueError('Constituency name cannot be empty')

    # Get the constituency or create one if necessary
    constituency = Constituency.query.filter(Constituency.name==cn).first()
    if constituency is None:
        constituency = Constituency(name=cn)
        session.add(constituency)

    # Delete any prior voting records for this constituency
    Voting.query.filter(Voting.constituency_id==constituency.id).delete()

    # Is there one result per party?
    if len(results) != len(set(p for _, p in results)):
        raise ValueError('Multiple results for one party')

    # Now add a voting record for each result
    for count, party_id in results:
        if party_id not in valid_codes:
            raise ValueError('Party code "{}" is unknown'.format(party_id))
        session.add(Voting(
            count=count, party_id=party_id, constituency=constituency))

class Diagnostic:
    """A diagnostic from parsing a file. Records the original line, a
    human-readable message and a 1-based line number.

    """
    def __init__(self, line, message, line_number):
        self.line = line
        self.message = message
        self.line_number = line_number

    def __str__(self):
        return "{}: bad result line '{}': {}".format(
            self.line_number, self.line.strip(), self.message
        )

def import_results(results_file, valid_codes=None, session=None):
    """Take a iterable which yields result lines and add them to the database.
    If session is None, the global db.session is used.

    If valid_codes is non-None, it is a set containing the party codes which are
    allowed in this database. If None, this set is queried from the database.

    .. note::

        This can take a relatively long time when adding several hundred
        results. Should this become a bottleneck, there are some optimisation
        opportunities.

    """
    session = session if session is not None else db.session
    valid_codes = (
        valid_codes if valid_codes is not None else
        _query_valid_party_codes(session)
    )

    diagnostics = []

    # This is a relatively straightforward but sub-optimal way to implement a
    # bulk insert. The main issue is that the DB is queried once per result to
    # see if the constituency exists. It would be preferable to do a single
    # query over all of the given constituency names to determine which ones are
    # present. This would make the flow of this function less obvious. For the
    # moment, leave the sub-optimal implementation but should we need to
    # re-visit this function as we deal with greater numbers of results the
    # strategy above should be tried.

    for line_idx, line in enumerate(results_file):
        try:
            add_constituency_result_line(
                line, valid_codes=valid_codes, session=session)
        except ValueError as e:
            diagnostics.append(Diagnostic(
                line, e.args[0] % e.args[1:], line_idx + 1
            ))

    # Log the fact that this import happened
    log('\n'.join([
        'Imported {} result line(s), {} diagnostic(s)'.format(
            line_idx+1, len(diagnostics)),
    ] + [str(d) for d in diagnostics]))

    return diagnostics

# Ensure that sqlite honours foreign key constraints
# http://stackoverflow.com/questions/2614984/a
@sqlalchemy_event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
