'''
Default configuration options.

Important: do not put *any* non-production safe config in here. Anything which
should be enabled only in development should go into the config.dev module.

'''
SITE_NAME='Psephology'
SQLALCHEMY_TRACK_MODIFICATIONS=False
DEBUG=False
