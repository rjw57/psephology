import click
from flask.cli import with_appcontext

from .model import db

cli = click.Group('psephology', help='Commands specific to psephology')

@cli.command('initdb')
@with_appcontext
def initdb_command():
    """Initialises the database with the schema."""
    db.create_all()

