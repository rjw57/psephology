from psephology.model import db, Party

# Some standard result lines
RESULT_LINES = """
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

def add_parties(session=None):
    """Add the parties required for RESULT_LINES."""
    session = session if session is not None else db.session
    for id_ in 'C L LD UKIP G Ind SNP'.split():
        session.add(Party(id=id_, name='The {} party'.format(id_)))

