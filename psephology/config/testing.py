"""
Configuration used when running tests. Uses an in-memory database.

"""
import logging
logging.warning('USING TESTING CONFIGURATION')

SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
TESTING = True
SECRET_KEY = 'not-very-secret'
