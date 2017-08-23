"""
The :py:mod:`.api` module provides a Flask blueprint which implements the JSON
API.

"""

from flask import Blueprint, jsonify, request, abort, flash
from sqlalchemy.orm import joinedload

from psephology.model import db, import_results, Constituency, Voting
from psephology import query

blueprint = Blueprint('api', __name__)

@blueprint.route('/stats')
def stats():
    return jsonify(
        constituency_count=Constituency.query.count(),
    )

@blueprint.route('/party_totals')
def party_totals():
    return jsonify(
        party_totals=dict([
            (party.id, dict(
                name=party.name,
                constituency_count=constituency_count
            ))
            for party, constituency_count in query.party_totals()
        ])
    )

@blueprint.route('/constituencies')
def constituencies():
    q = query.constituency_winners().options(joinedload(Voting.party))
    return jsonify(
        constituencies=[
            dict(
                name=c.name,
                party=dict(
                    name=v.party.name, id=v.party.id
                ) if v is not None else None,
                maximum_votes=max_v,
                total_votes=tot_v,
                share_percentage=(
                    (100. * max_v) / tot_v
                    if max_v is not None else None
                ),
            )
            for c, v, max_v, tot_v in q
        ]
    )

@blueprint.route('/import', methods=['POST'])
def import_():
    # Interpret incoming data as UTF-8 text. If this fails, abort with a 400 Bad
    # Request error.
    try:
        results = request.data.decode('utf8').strip().splitlines()
    except UnicodeDecodeError:
        abort(400)

    diagnostics = import_results(results)
    db.session.commit()

    return jsonify(
        diagnostics=[
            dict(line=d.line, message=d.message, line_number=d.line_number)
            for d in diagnostics
        ],
        line_count=len(results),
    )
