from psephology.model import db, Constituency

from .fixtures import RESULT_LINES, add_parties
from .util import TestCase

class StatsAPITests(TestCase):
    def test_constituency_counts(self):
        """Constituency counts are present"""
        r = self.client.get('/api/stats').json
        self.assertEqual(r.get('constituency_count'), 0)

        db.session.add(Constituency(name='C'))
        db.session.commit()

        r = self.client.get('/api/stats').json
        self.assertEqual(r.get('constituency_count'), 1)

class ImportAPITests(TestCase):
    def setUp(self):
        super(ImportAPITests, self).setUp()

        # dd the parties required to parse RESULT_LINES
        add_parties()
        db.session.commit()

    def test_requires_post(self):
        """The import API endpoint is POST-only."""
        r = self.client.get('/api/import')
        self.assertEqual(r.status_code, 405)

    def test_basic_usage(self):
        """The import API's basic usage works."""
        data = '\n'.join(RESULT_LINES)
        r = self.client.post('/api/import', data=data).json
        self.assertIn('diagnostics', r)
        self.assertEqual(len(r['diagnostics']), 4)
        self.assertIn('line_count', r)
        self.assertEqual(r['line_count'], 31)

        for d in r['diagnostics']:
            self.assertIn('line_number', d)
            self.assertIn('line', d)
            self.assertIn('message', d)

        self.assertEqual(r['diagnostics'][0]['line_number'], 5)
        self.assertEqual(r['diagnostics'][1]['line_number'], 8)
        self.assertEqual(r['diagnostics'][2]['line_number'], 12)
        self.assertEqual(r['diagnostics'][3]['line_number'], 16)

        # Check correct number of constituencies imported
        self.assertEqual(Constituency.query.count(), 29)

