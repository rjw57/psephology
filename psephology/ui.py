from flask import (
    Blueprint, current_app, render_template,
)
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from .model import db, Voting, Constituency

blueprint = Blueprint('ui', __name__, template_folder='templates/ui')

@blueprint.route('/')
def index():
    results = (
        db.session.query(Voting, func.max(Voting.count), func.sum(Voting.count))
        .select_from(Voting)
        .join(Constituency)
        .group_by(Constituency).order_by(Constituency.name)
        .options(
            joinedload(Voting.constituency),
            joinedload(Voting.party)
        )
    )
    return render_template('index.html', results=results)
