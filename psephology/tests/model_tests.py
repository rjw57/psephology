import logging
import unittest

from flask import current_app

import flask_migrate
from flask_testing import TestCase as FlaskTestCase

from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from psephology.app import create_app
from psephology.model import (
    db, migrate, Party, Constituency, Voting,
    add_constituency_result_line, import_results,
)

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
    def test_creation(self):
        """Parties can be created and persisted into the database."""
        db.create_all()
        p = Party(id='X')
        db.session.add(p)
        db.session.commit()
        self.assertEqual(Party.query.filter(Party.id=='X').count(), 1)

    def test_name_unique(self):
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

class ConstituencyTests(TestCase):
    def test_creation(self):
        """Constituencies can be created."""
        c = Constituency(name='foo')
        db.session.add(c)
        db.session.commit()
        self.assertEqual(
            Constituency.query.filter(Constituency.name=='foo').count(), 1)

    def test_name_unique(self):
        """Constituencies should not allow duplicate names."""
        p1 = Constituency(name='Foo')
        p2 = Constituency(name='Bar')
        db.session.add(p1)
        db.session.add(p2)
        db.session.commit() # ok

        p3 = Constituency(name='Foo')
        db.session.add(p3)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_need_name(self):
        """Constituencies need a name."""
        c = Constituency()
        db.session.add(c)
        with self.assertRaises(IntegrityError):
            db.session.commit()

class VotingTests(TestCase):
    def setUp(self):
        super(VotingTests, self).setUp()

        # Create some constituency and party fixtures
        db.session.add(Constituency(id=1, name='C1'))
        db.session.add(Constituency(id=2, name='C2'))
        db.session.add(Party(id='P1', name='Party 1'))
        db.session.add(Party(id='P2', name='Party 2'))
        db.session.commit()

    def test_creation(self):
        """Voting records can be created."""
        v = Voting(count=10, constituency_id=1, party_id='P1')
        db.session.add(v)
        db.session.commit()
        self.assertIsNot(v.id, None)

    def test_relations(self):
        """Voting records should have a constituency and party relation."""
        v = Voting(count=10, constituency_id=1, party_id='P2')
        db.session.add(v)
        db.session.commit()

        v = Voting.query.get(v.id)
        self.assertEqual(v.constituency.name, 'C1')
        self.assertEqual(v.party.name, 'Party 2')

        self.assertIn(v.id, [v2.id for v2 in Constituency.query.get(1).votings])
        self.assertIn(v.id, [v2.id for v2 in Party.query.get('P2').votings])

    def test_constituency_required(self):
        """Voting records require a constituency."""
        v = Voting(count=10, party_id=2)
        db.session.add(v)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_party_required(self):
        """Voting records require a party."""
        v = Voting(count=10, constituency_id=2)
        db.session.add(v)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_count_required(self):
        """Voting records require a count."""
        v = Voting(party_id=1, constituency_id=2)
        db.session.add(v)
        with self.assertRaises(IntegrityError):
            db.session.commit()

class AddResultLineTests(TestCase):
    def setUp(self):
        super(AddResultLineTests, self).setUp()

        # Create some constituency and party fixtures
        db.session.add(Constituency(id=1, name='C1'))
        db.session.add(Constituency(id=2, name='C2'))
        db.session.add(Party(id='P1', name='Party 1'))
        db.session.add(Party(id='P2', name='Party 2'))
        db.session.add(Party(id='P3', name='Party 3'))
        db.session.commit()

    def test_simple_usage(self):
        """Simple addition of result line should work."""
        add_constituency_result_line('C1, 10, P1, 20, P2')
        db.session.commit()

        q = Voting.query.filter(Voting.constituency_id==1)
        self.assertEqual(q.count(), 2)

        self.assertEqual(q.filter(Voting.party_id=='P1').count(), 1)
        self.assertEqual(q.filter(Voting.party_id=='P2').count(), 1)

        self.assertEqual(q.filter(Voting.party_id=='P1').first().count, 10)
        self.assertEqual(q.filter(Voting.party_id=='P2').first().count, 20)

    def test_replaces_prior_result(self):
        """Adding a result replaces the previous one."""
        add_constituency_result_line('C1, 10, P1, 20, P2')
        db.session.commit()
        add_constituency_result_line('C1, 12, P3, 11, P1')
        db.session.commit()

        q = Voting.query.filter(Voting.constituency_id==1)
        self.assertEqual(q.count(), 2)

        self.assertEqual(q.filter(Voting.party_id=='P1').count(), 1)
        self.assertEqual(q.filter(Voting.party_id=='P2').count(), 0)
        self.assertEqual(q.filter(Voting.party_id=='P3').count(), 1)

        self.assertEqual(q.filter(Voting.party_id=='P1').first().count, 11)
        self.assertEqual(q.filter(Voting.party_id=='P3').first().count, 12)

    def test_empty_constituency_fails(self):
        """An empty constituency name is invalid"""
        with self.assertRaises(ValueError):
            add_constituency_result_line(', 10, P1, 20, P2')

    def test_non_existent_party_fails(self):
        """An non-existent party is invalid"""
        with self.assertRaises(ValueError):
            add_constituency_result_line('C1, 10, NOTEXIST')

    def test_creates_constituency(self):
        """An unknown constituency is created automatically."""
        add_constituency_result_line('New, and exciting, constituency, 10, P1, 20, P2')
        db.session.commit()

        c = Constituency.query.filter(
            Constituency.name=='New, and exciting, constituency').first()
        self.assertIsNot(c, None)

        q = Voting.query.filter(Voting.constituency==c)
        self.assertEqual(q.count(), 2)

        self.assertEqual(q.filter(Voting.party_id=='P1').count(), 1)
        self.assertEqual(q.filter(Voting.party_id=='P2').count(), 1)

        self.assertEqual(q.filter(Voting.party_id=='P1').first().count, 10)
        self.assertEqual(q.filter(Voting.party_id=='P2').first().count, 20)

    def test_multiple_party_fails(self):
        """Multiple results for one party are not allowed."""
        with self.assertRaises(ValueError):
            add_constituency_result_line('C1, 10, P1, 20, P1')

class ImportDataTest(TestCase):
    """Test import_results functionality."""
    def setUp(self):
        super(ImportDataTest, self).setUp()

        # Create some party fixtures
        for id_ in 'C L LD UKIP G Ind SNP'.split():
            db.session.add(Party(id=id_, name='The {} party'.format(id_)))
        db.session.commit()

    def test_diagnostics(self):
        """Importing some known bad results should give diagnostics."""
        diagnostics = import_results(RESULTS)
        print('\n'.join(str(s) for s in diagnostics))
        self.assertEqual(len(diagnostics), 4)
        self.assertEqual(diagnostics[0].line_number, 5)
        self.assertEqual(diagnostics[1].line_number, 8)
        self.assertEqual(diagnostics[2].line_number, 12)
        self.assertEqual(diagnostics[3].line_number, 16)

    def test_idempotent(self):
        """Importing the same results twice should not change number of voting
        records."""
        diagnostics = import_results(RESULTS[:4])
        self.assertEqual(len(diagnostics), 0)
        self.assertEqual(Voting.query.count(), 20)
        diagnostics = import_results(RESULTS[:4])
        self.assertEqual(len(diagnostics), 0)
        self.assertEqual(Voting.query.count(), 20)

    def test_replace(self):
        """Importing a new result line should entirely replace previous one."""
        diagnostics = import_results(RESULTS[:4])
        self.assertEqual(len(diagnostics), 0)

        c = Constituency.query.filter(Constituency.name=='Braintree').first()
        self.assertIsNot(c, None)

        p = Party.query.get('C')

        self.assertEqual(
            Voting.query.filter(
                Voting.constituency==c, Voting.party==p
            ).first().count, 32873)
        self.assertEqual(
            Voting.query.filter(
                Voting.constituency==c).count(), 5)

        diagnostics = import_results(['Braintree, 123, C'])
        self.assertEqual(len(diagnostics), 0)

        self.assertEqual(
            Voting.query.filter(
                Voting.constituency==c, Voting.party==p
            ).first().count, 123)
        self.assertEqual(
            Voting.query.filter(
                Voting.constituency==c).count(), 1)


RESULTS = """
Barrow and Furness, 22383, C, 22592, L, 962, UKIP, 1278, LD, 375, G
Braintree, 32873, C, 14451, L, 1835, UKIP, 2251, LD, 916, G
Bristol South, 16679, C, 32666, L, 1672, UKIP, 1821, LD, 1428, G
Broadland, 32406, C, 16590, L, 1594, UKIP, 4449, LD, 932, G
Burton, 28936, C, 18889, X, 1262, LD, 824, G
Dumfriesshire, Clydesdale and Tweeddale, 24177, C, 8102, L, 1949, LD, 14736, SNP
East Hampshire, 35263, C, 9411, L, 8403, LD, 1760, G

Edinburgh South West, 16478, C, 13213, L, 2124, LD, 17575, SNP
Edmonton, 10106, C, 31221, L, 860, UKIP, 858, LD, 633, G
Grantham and Stamford, 35090, C, 14996, L, 1745, UKIP, 3120, LD, 782, G
, 15566, C, 25740, L, 2591, UKIP, 912, LD
Hemsworth, 15566, C, 25740, L, 2591, UKIP, 912, LD
Hornsey and Wood Green, 9246, C, 40738, L, 429, UKIP, 10000, LD, 1181, G
Lagan Valley, 462, C
Llanelli, 9544, C, 21568, L, 1331, UKIP, 548, LD, 548, LD
North Antrim
North East Cambridgeshire, 34340, C, 13070, L, 2174, UKIP, 2383, LD, 1024, G
Oxford East, 11834, C, 35118, L, 4904, LD, 1785, G
Pudsey, 25550, C, 25219, L, 1761, LD
Reigate, 30896, C, 13282, L, 1542, UKIP, 5889, LD, 2214, G
Rhondda, 3333, C, 21096, L, 880, UKIP, 277, LD
Rossendale and Darwen, 25499, C, 22283, L, 1550, LD, 824, G
Rushcliffe, 30223, C, 22213, L, 1490, UKIP, 2759, LD, 1626, G
Rutherglen and Hamilton West, 9941, C, 19101, L, 465, UKIP, 2158, LD, 18836, SNP
South Down
Stevenage, 24798, C, 21412, L, 2032, LD, 1085, G
Sunderland Central, 15059, C, 25056, L, 2209, UKIP, 1777, LD, 705, G
Thurrock, 19880, C, 19535, L, 10112, UKIP, 798, LD
Wolverhampton North East, 14695, C, 19282, L, 1479, UKIP, 570, LD, 482, G
Workington, 17392, C, 21317, L, 1556, UKIP, 1133, LD
""".strip().splitlines()

if __name__ == '__main__':
    unittest.main()
