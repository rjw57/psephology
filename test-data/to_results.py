#!/usr/bin/env python3

"""
Parse GE2017 result into a results file suitable for passing to psephology.

Usage:
    to_results.py <input> <output>

Options:
    -h --help       Show a usage summary
    <input>         Input CSV file
    <output>        Output results file

"""
from collections import namedtuple
import csv
import docopt

# Mapping from psephology party codes to CSV header. Note there is no
# independent column
PARTY_MAPPINGS = {
    'C': 'con', 'L': 'lab', 'UKIP': 'ukip', 'LD': 'ld', 'G': 'green',
    'SNP': 'snp',
}

def main():
    opts = docopt.docopt(__doc__)

    with open(opts['<input>']) as in_f, open(opts['<output>'], 'w') as out_f:
        reader = csv.reader(in_f)

        # Create a named tuple representing a row record
        Record = namedtuple('Record', next(reader))

        # For each row in the input...
        for row in reader:
            # Put the row into the namedtuple so that we can extract values
            record = Record(*row)

            # Initialise an empty row list
            results = {}

            # Pick out each party's result. Ignore parties who got no votes in
            # that constituency.
            for code, column in PARTY_MAPPINGS.items():
                count = int(getattr(record, column))
                if count == 0:
                    continue
                results[code] = count

            # Write result line
            out_f.write(', '.join(
                [record.constituency_name] +
                [
                    '{}, {}'.format(count, party)
                    for party, count in results.items()
                ]
            ))
            out_f.write('\n')

if __name__ == '__main__':
    main()
