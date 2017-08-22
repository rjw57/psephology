"""
Some potted database queries

"""
from sqlalchemy import func

from .model import db, Constituency, Party, Voting

def constituency_winners():
    """
    A query which returns the Constituency, Voting, winning vote count and
    total vote count for each constituency. If there was no winner in the
    constituency, then the Voting, winning vote count and total vote count is
    None.

    The maximum vote count for a constituency is labelled 'max_vote_count' and
    the total vote count is labelled 'total_vote_count'.

    If you intend to get related objects from the Voting, make sure to add an
    appropriate joinedload() to the options.

    E.g.:

    .. code:: python

        q = constituency_winners().options(
            joinedload(Voting.party)
        )

    """
    return (
        Constituency.query
        .add_entity(Voting)
        .add_columns(
            func.max(Voting.count).label('max_vote_count'),
            func.sum(Voting.count).label('total_vote_count')
        )
        .outerjoin(Voting).group_by(Constituency.id)
    )

def party_totals():
    """
    A query which returns a Party and a constituency count, labelled
    'constituency_count' which gives the number of constituencies that party has
    won.

    """
    q = (
        constituency_winners().add_columns(Voting.party_id.label('party_id'))
        .subquery(with_labels=True, reduce_columns=True)
    )
    return (
        Party.query.add_columns(func.count().label('constituency_count'))
        .join(q).group_by(q.c.party_id)
    )
