from flask_testing import TestCase as FlaskTestCase
from psephology.app import create_app
from psephology.model import db

class TestCase(FlaskTestCase):
    """Common TestCase sub-class for API test fixtures."""

    def create_app(self):
        app = create_app(config_object='psephology.config.testing')
        self.client = app.test_client()
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
