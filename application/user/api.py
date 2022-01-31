from flask import Blueprint, request, abort, render_template
from flask_login import current_user

from application import db
from .models import Well

api = Blueprint('api', __name__)


@api.route('/estimate', methods=['GET', 'POST'])
def well_estimate():
    if not current_user.is_authenticated:
        abort(401)
    if request.method == 'POST':
        well_name = request.form['wellName']
        well = Well(name=well_name, client=current_user)
        db.session.add(well)
        db.session.commit()
        return 'Success', 200
    html = ''
    for well in current_user.wells:
        template = render_template('dashboard-card.html', well=well)
        html += template

    return html, 200
