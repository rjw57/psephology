from psephology.config.default import *
from psephology._util import token_urlsafe

SQLALCHEMY_DATABASE_URI='sqlite:////usr/src/app/psephology.sqlite'
SECRET_KEY=token_urlsafe()
