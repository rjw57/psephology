"""
The :py:mod:`.io` module provides functions which can be used to parse external
data formats used by Psephology.

"""

def parse_result_line(line):
    """Take a line consisting of a constituency name and vote count, party id
    pairs all separated by commas and return the constituency name and a list of
    results as a pair. The results list consists of vote-count party name pairs.

    To handle constituencies whose names include a comma, the parse considers
    count, party pairs *from the right* and stops when it reaches a vote count
    which is not an integer.

    """
    items = line.strip().split(',')

    results = []

    # If there is more to parse, there should be at least the constituency name,
    # a vote count and a party id, i.e. more than two values
    while len(items) > 2:
        party_id = items.pop()
        count_str = items.pop()
        try:
            count = int(count_str.strip())
        except ValueError:
            items.extend([count_str, party_id])
            break
        results.append((count, party_id.strip()))

    # The remaining items are assumed to be to be the constituency name. Note we
    # need to reverse the results in order to preserve the order we were given.
    return ','.join(items), results[::-1]
