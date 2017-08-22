from flask import (
    Blueprint, current_app, render_template, redirect, url_for
)
from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from psephology.model import db, Voting, Constituency
import psephology.query as query

blueprint = Blueprint('ui', __name__, template_folder='templates/ui')

@blueprint.route('/')
def index():
    return redirect(url_for('ui.summary'))

@blueprint.route('/summary')
def summary():
    results = (
        query.party_totals()
        .order_by(desc('constituency_count'))
    )
    return render_template('summary.html', results=results)

@blueprint.route('/constituencies')
def constituencies():
    results = (
        query.constituency_winners().order_by(Constituency.name)
        .options(
            joinedload(Voting.party)
        )
    )
    return render_template('constituencies.html', results=results)
