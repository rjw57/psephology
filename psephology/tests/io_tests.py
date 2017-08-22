import unittest
from psephology import io

class ResultLineTest(unittest.TestCase):
    def test_basic_parsing(self):
        """Parsing a straightforward line should succeed."""
        cn, results = io.parse_result_line('Littleton, 10, C, 11, L')
        self.assertEqual(cn, 'Littleton')
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], (10, 'C'))
        self.assertEqual(results[1], (11, 'L'))

    def test_empty_string(self):
        """An empty result line gives an empty parse."""
        cn, results = io.parse_result_line('')
        self.assertEqual(cn, '')
        self.assertEqual(len(results), 0)

    def test_odd_whitespace(self):
        """Odd whitespace characters do not affect the parsing."""
        cn, results = io.parse_result_line(
            '    Littleton,    10,   C,  \t11,     L\n')
        self.assertEqual(cn, 'Littleton')
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], (10, 'C'))
        self.assertEqual(results[1], (11, 'L'))

    def test_no_results(self):
        """No results for a constituency is still parseable."""
        cn, results = io.parse_result_line('Whiskey on Rye')
        self.assertEqual(cn, 'Whiskey on Rye')
        self.assertEqual(len(results), 0)

    def test_constituency_with_comma(self):
        """A constituency with a comma is handled gracefully."""
        cn, results = io.parse_result_line('''
            Birmingham, City of, Edgbaston, 10, C, 11, L, 12, LD''')
        self.assertEqual(cn, 'Birmingham, City of, Edgbaston')
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0], (10, 'C'))
        self.assertEqual(results[1], (11, 'L'))
        self.assertEqual(results[2], (12, 'LD'))

    def test_constituency_with_number(self):
        """A constituency with a number is handled gracefully."""
        cn, results = io.parse_result_line('''
            Direction, The band, 1, 10, C, 11, L, 12, LD''')
        self.assertEqual(cn, 'Direction, The band, 1')
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0], (10, 'C'))
        self.assertEqual(results[1], (11, 'L'))
        self.assertEqual(results[2], (12, 'LD'))

    def test_multiple_results(self):
        """Multiple results for one party are handled gracefully."""
        cn, results = io.parse_result_line('Littleton, 10, C, 9, L, 11, C, 12, C')
        self.assertEqual(cn, 'Littleton')
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0], (10, 'C'))
        self.assertEqual(results[1], (9, 'L'))
        self.assertEqual(results[2], (11, 'C'))
        self.assertEqual(results[3], (12, 'C'))


