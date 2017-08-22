from flask import (
    Blueprint, current_app,
)

from .model import db

blueprint = Blueprint('ui', __name__, template_folder='templates/ui')

@blueprint.route('/')
def index():
    return render_template('index.html')
