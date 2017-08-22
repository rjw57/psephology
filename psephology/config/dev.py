'''
Configuration specific to development environment. Do *not* use this
configuration in production.

'''
import os
import logging

from flask.helpers import get_root_path
from psephology._util import token_urlsafe

logging.warning('Using development config. DO NOT DO THIS IN PRODUCTION.')

DEBUG=True
SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(
    get_root_path('psephology'), 'db.sqlite')
SECRET_KEY=token_urlsafe()
DEBUG_TB_INTERCEPT_REDIRECTS=False
