from io import BytesIO
from bs4 import BeautifulSoup

from psephology.model import db, add_constituency_result_line, log
from .util import TestCase
from .fixtures import add_parties

class UITests(TestCase):
    def setUp(self):
        super(UITests, self).setUp()

        # Create some party fixtures
        add_parties()
        db.session.commit()

    def test_index(self):
        """There is something returned for the index page but it is a
        redirect."""
        r = self.client.get('/')
        self.assertEqual(r.status_code, 302)

    def test_summary_no_results(self):
        """Summary with no results should have UI element saying so."""
        r = self.client.get('/summary')
        self.assertEqual(r.status_code, 200)
        soup = BeautifulSoup(r.data, 'html.parser')
        self.assertIsNot(soup.find(id='no-results'), None)
        self.assertIs(soup.find(id='results-table'), None)

    def test_summary_with_results(self):
        """Summary with results should have a table."""
        add_constituency_result_line('X, 10, C')
        r = self.client.get('/summary')
        self.assertEqual(r.status_code, 200)
        soup = BeautifulSoup(r.data, 'html.parser')
        self.assertIs(soup.find(id='no-results'), None)
        self.assertIsNot(soup.find(id='results-table'), None)

    def test_constituency_no_results(self):
        """Summary with no results should have UI element saying so."""
        r = self.client.get('/constituencies')
        self.assertEqual(r.status_code, 200)
        soup = BeautifulSoup(r.data, 'html.parser')
        self.assertIsNot(soup.find(id='no-results'), None)

    def test_constituency_with_results(self):
        """Summary with results should have a table."""
        add_constituency_result_line('X, 10, C')
        r = self.client.get('/constituencies')
        self.assertEqual(r.status_code, 200)
        soup = BeautifulSoup(r.data, 'html.parser')
        self.assertIs(soup.find(id='no-results'), None)
        self.assertIsNot(soup.find(id='results-table'), None)

    def test_log_no_results(self):
        """Log with no results should have UI element saying so."""
        r = self.client.get('/log')
        self.assertEqual(r.status_code, 200)
        soup = BeautifulSoup(r.data, 'html.parser')
        self.assertIsNot(soup.find(id='no-results'), None)
        self.assertIs(soup.find(id='log'), None)

    def test_log_with_results(self):
        """Log with results should have a table."""
        log('hello')
        r = self.client.get('/log')
        self.assertEqual(r.status_code, 200)
        soup = BeautifulSoup(r.data, 'html.parser')
        self.assertIs(soup.find(id='no-results'), None)
        self.assertIsNot(soup.find(id='log'), None)

    def test_export(self):
        """Can get back a line from export."""
        add_constituency_result_line('X, 10, C')
        r = self.client.get('/export/results')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.decode('utf8').strip(), 'X, 10, C')

    def test_import(self):
        """Import form renders"""
        r = self.client.get('/import')
        self.assertEqual(r.status_code, 200)

    def test_import_with_bad_utf8(self):
        """Import results with bad UTF8 gives HTTP 400"""
        r = self.client.post('/import/results', data={
            'results': (BytesIO(b'foo\x80'), 'foo.txt'),
        })
        self.assertEqual(r.status_code, 400)

    def test_import_results(self):
        """Import results"""
        r = self.client.post('/import/results', data={
            'results': (BytesIO(b'X, 10, C'), 'foo.txt'),
        })
        # If import succeeds then there should be a re-direct
        self.assertEqual(r.status_code, 302)
