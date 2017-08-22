import functools
import logging
import unittest

from flask import current_app

import flask_migrate
from flask_testing import TestCase as FlaskTestCase
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from psephology.app import create_app
from psephology.model import db, migrate, Party

class TestCase(FlaskTestCase):
    """Common TestCase sub-class for DB test fixtures."""

    def create_app(self):
        app = create_app(config_object='psephology.config.testing')
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()

class PartyTests(TestCase):
    def test_party_creation(self):
        """Parties can be created and persisted into the database."""
        p = Party(id='X')
        db.session.add(p)
        db.session.commit()
        self.assertEqual(Party.query.filter(Party.id=='X').count(), 1)

    def test_party_name_unique(self):
        """Parties should not allow duplicate names."""
        p1 = Party(id='Fo', name='Foo')
        p2 = Party(id='B', name='Bar')
        db.session.add(p1)
        db.session.add(p2)
        db.session.commit() # ok

        p3 = Party(id='F', name='Foo')
        db.session.add(p3)
        with self.assertRaises(IntegrityError):
            db.session.commit()

if __name__ == '__main__':
    unittest.main()
