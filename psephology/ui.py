from flask import (
    Blueprint, current_app, render_template, redirect, url_for,
    request, abort, flash, Response
)
from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from psephology.model import (
    db, Voting, Constituency, LogEntry,
    import_results as model_import_results
)
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
    ).all()
    return render_template('summary.html', results=results)

@blueprint.route('/constituencies')
def constituencies():
    results = (
        query.constituency_winners().order_by(Constituency.name)
        .options(
            joinedload(Voting.party)
        )
    ).all()
    return render_template('constituencies.html', results=results)

@blueprint.route('/log')
def log():
    results = (
        LogEntry.query.order_by(desc(LogEntry.created_at))
    ).all()
    return render_template('log.html', results=results)

@blueprint.route('/import')
def import_form():
    return render_template('import.html')

@blueprint.route('/import/results', methods=['POST'])
def import_results():
    # Get results file from request
    fobj = request.files.get('results')
    if fobj is None:
        abort(400)

    # Interpret incoming data as UTF-8 text. If this fails, abort with a 400 Bad
    # Request error.
    data = fobj.read()
    try:
        results = data.decode('utf8').strip().splitlines()
    except UnicodeDecodeError:
        abort(400)

    diagnostics = model_import_results(results)
    db.session.commit()

    flash('Processed {} line(s) with {} issue(s)'.format(
        len(results), len(diagnostics)))

    # Redirect to the index
    return redirect(url_for('ui.index'))

@blueprint.route('/export/results')
def export_results():
    q = Constituency.query.options(joinedload(Constituency.votings))
    output = []
    for con in q:
        output.append(', '.join(
            [con.name] + [
                '{}, {}'.format(v.count, v.party_id)
                for v in con.votings
            ]
        ))
    return Response('\n'.join(output), mimetype='text/plain')
