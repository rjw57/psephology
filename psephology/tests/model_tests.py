from flask import current_app
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from psephology.model import (
    db, migrate, Party, Constituency, Voting,
    add_constituency_result_line, import_results,
)

from .fixtures import RESULT_LINES, add_parties
from .util import TestCase

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

    def test_no_results_adds_constituency(self):
        """A constituency with no results is still added."""
        add_constituency_result_line('XXX')
        db.session.commit()
        self.assertEqual(
            Constituency.query.filter(Constituency.name=='XXX').count(), 1)

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
        add_parties()
        db.session.commit()

    def test_diagnostics(self):
        """Importing some known bad results should give diagnostics."""
        diagnostics = import_results(RESULT_LINES)
        print('\n'.join(str(s) for s in diagnostics))
        self.assertEqual(len(diagnostics), 4)
        self.assertEqual(diagnostics[0].line_number, 5)
        self.assertEqual(diagnostics[1].line_number, 8)
        self.assertEqual(diagnostics[2].line_number, 12)
        self.assertEqual(diagnostics[3].line_number, 16)

    def test_idempotent(self):
        """Importing the same results twice should not change number of voting
        records."""
        diagnostics = import_results(RESULT_LINES[:4])
        self.assertEqual(len(diagnostics), 0)
        self.assertEqual(Voting.query.count(), 20)
        diagnostics = import_results(RESULT_LINES[:4])
        self.assertEqual(len(diagnostics), 0)
        self.assertEqual(Voting.query.count(), 20)

    def test_replace(self):
        """Importing a new result line should entirely replace previous one."""
        diagnostics = import_results(RESULT_LINES[:4])
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
