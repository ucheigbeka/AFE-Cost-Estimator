from urllib.parse import urljoin

from flask import Blueprint, render_template, request, url_for

from application.utils import id_to_model
from .api import api
from .models import model_mapping

admin = Blueprint('admin', __name__)
admin.register_blueprint(api, url_prefix='/api')


def generate_options(_id):
    cls = id_to_model(_id)
    fields = cls.generate_fields(exclude_id=_id == 'well-cost')
    fields.append({'type': 'control'})

    return fields, 'admin.admin_api.' + _id.replace('-', '_')


@admin.route('/')
def editor():
    if request.args.get('id'):
        _id = request.args.get('id')
        fields, endpoint = generate_options(_id)
        url = urljoin(request.root_url, url_for(endpoint))
        return {'fields': fields, 'url': url}, 200

    return render_template('admin/editor.html', nav_items=model_mapping), 200
