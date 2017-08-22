import click
from flask.cli import with_appcontext

from .model import import_results, db

cli = click.Group('psephology', help='Commands specific to psephology')

@cli.command('importresults')
@click.argument('results_file', type=click.File('r'))
@with_appcontext
def importresults(results_file):
    """Ingest a results file into the database."""
    diagnostics = import_results(results_file)
    for diagnostic in diagnostics:
        logging.warning(str(diagnostic))
    db.session.commit()
