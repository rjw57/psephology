"""
The :py:mod:`.app` module provides support for creating Flask Application
objects.

"""

from flask import Flask

from .api import blueprint as api
from .ui import blueprint as ui
from .model import db, migrate
from .cli import cli

def create_app(config_filename=None, config_object=None):
    """
    Create a new application object. The database and CLI are automatically
    wired up. If ``config_filename`` or ``config_object`` are not ``None`` they
    are passed to :py:func:`app.config.from_pyfile` and
    :py:func:`app.config.from_object` respectively.

    Returns the newly created application object.

    """
    app = Flask(__name__)

    app.config.from_object('psephology.config.default')
    if config_filename is not None:
        app.config.from_pyfile(config_filename)
    if config_object is not None:
        app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    app.register_blueprint(ui)
    app.register_blueprint(api, url_prefix='/api')
    app.cli.add_command(cli)

    # Things which should only be present in DEBUG-enabled apps
    app.debug = app.config.get('DEBUG', False)
    if app.debug:
        from flask_debugtoolbar import DebugToolbarExtension
        toolbar = DebugToolbarExtension()
        toolbar.init_app(app)

    return app
