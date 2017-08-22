from sqlite3 import Connection as SQLite3Connection

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event as sqlalchemy_event, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import DEFAULT_NAMING_CONVENTION

# Create the shared database and migration singletons.
db = SQLAlchemy(
    metadata=MetaData(naming_convention=DEFAULT_NAMING_CONVENTION)
)
migrate = Migrate()

class Party(db.Model):
    """A political party. Each party is primarily keyed by its abbreviation. In
    addition, the name of a political party should be unique.

    """
    __tablename__ = 'parties'

    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, unique=True)

# Ensure that sqlite honours foreign key constraints
# http://stackoverflow.com/questions/2614984/a
@sqlalchemy_event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
