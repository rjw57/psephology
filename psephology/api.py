"""
Blueprint implementing API.

"""

from flask import Blueprint, jsonify, request
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from .model import db, import_results, Constituency

blueprint = Blueprint('api', __name__)

@blueprint.route('/stats')
def index():
    return jsonify(
        constituency_count=Constituency.query.count(),
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
