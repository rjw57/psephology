from psephology.model import (
    db, add_constituency_result_line, Constituency, Party
)
from psephology import query

from .fixtures import add_parties
from .util import TestCase

class ConstituencyWinnersTests(TestCase):
    def setUp(self):
        super(ConstituencyWinnersTests, self).setUp()

        # dd the parties required to parse RESULT_LINES
        add_parties()
        db.session.commit()

    def test_result_for_every_constituency(self):
        """All constituencies get winners even if no results."""
        add_constituency_result_line('A, 10, C, 20, L')
        add_constituency_result_line('B')
        self.assertEqual(
            query.constituency_winners().count(), 2)

    def test_winners_correct(self):
        """Test that the winners are correct."""
        add_constituency_result_line('A, 10, C, 20, L')
        add_constituency_result_line('B')
        add_constituency_result_line('C, 200, C, 100, L')

        c, v, max_v, tot_v = (
            query.constituency_winners().filter(Constituency.name=='A').one())
        self.assertEqual(v.party.id, 'L')
        self.assertEqual(max_v, 20)
        self.assertEqual(tot_v, 30)

        c, v, max_v, tot_v = (
            query.constituency_winners().filter(Constituency.name=='B').one())
        self.assertIs(v, None)
        self.assertIs(max_v, None)
        self.assertIs(tot_v, None)

        c, v, max_v, tot_v = (
            query.constituency_winners().filter(Constituency.name=='C').one())
        self.assertEqual(v.party.id, 'C')
        self.assertEqual(max_v, 200)
        self.assertEqual(tot_v, 300)

class PartyTotalsTests(TestCase):
    def setUp(self):
        super(PartyTotalsTests, self).setUp()

        # dd the parties required to parse RESULT_LINES
        add_parties()
        db.session.commit()

    def test_basic(self):
        """Basic usage gives sane results."""

        # C ends up with 1 seat, L with 3
        add_constituency_result_line('A, 10, C, 20, L')
        add_constituency_result_line('B, 30, C, 40, L')
        add_constituency_result_line('C, 10, C, 50, L')
        add_constituency_result_line('D, 20, C, 2, L')
        add_constituency_result_line('E')

        p, tot = query.party_totals().filter(Party.id=='L').one()
        self.assertEqual(tot, 3)
        p, tot = query.party_totals().filter(Party.id=='C').one()
        self.assertEqual(tot, 1)
