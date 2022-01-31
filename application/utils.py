from threading import Thread
from urllib.parse import urlparse, urljoin

from flask import request, url_for
from itsdangerous.url_safe import URLSafeTimedSerializer
from itsdangerous.exc import SignatureExpired, BadSignature
from openpyxl import load_workbook

from . import app, db, ma, mail

acct_activate_url_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='activate')
acct_reset_url_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='reset')


def _launch_task(func, *args, **kwargs):
    # TODO: Integrate `Celery` or `Redis` for scheduling background tasks
    Thread(target=func, args=args, kwargs=kwargs).start()


def model_to_id(model):
    return model.__tablename__.replace('_', '-')


def get_model_from_tablename(tablename):
    for mapper in db.Model.registry.mappers:
        cls = mapper.class_
        if cls.__tablename__ == tablename:
            return cls


def id_to_model(_id):
    tablename = _id.replace('-', '_')
    return get_model_from_tablename(tablename)


def load_marshmallow_schema(model):
    model = model if isinstance(model, str) else model.__name__
    try:
        exec(f'from application.admin.models import {model}Schema')
    except ModuleNotFoundError:
        return
    return locals().get(f'{model}Schema')


def get_table_columns(_id=None, model: db.Model = None, schema: ma.SQLAlchemyAutoSchema = None):
    model = model if model else id_to_model(_id)
    schema = schema if schema else load_marshmallow_schema(model)
    columns = schema._declared_fields.keys() if schema else model.__table__.columns.keys()

    return list(columns)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    target_url = urlparse(urljoin(request.host_url, target))
    return target_url.scheme in ('http', 'https') and target_url.netloc == ref_url.netloc


def generate_signed_url(uid, action):
    serializer = acct_reset_url_serializer if action == 'reset' else acct_activate_url_serializer
    return urljoin(request.base_url, url_for(action, token=serializer.dumps([uid])))


def validate_signature(payload, action):
    serializer = acct_reset_url_serializer if action == 'reset' else acct_activate_url_serializer
    try:
        uid = serializer.loads(payload, max_age=10 * 60)
    except BadSignature:
        return False, 'Bad signature'
    except SignatureExpired:
        return False, 'Signature expired'

    return True, uid


def send_email(msg, max_tries=3):
    # TODO: Make asynchronous
    for _ in range(max_tries):
        try:
            mail.send(msg)
            return True
        except TimeoutError:
            pass
    return False


def parse_xl(file_obj, columns, with_header=True):
    workbook = load_workbook(file_obj, read_only=True, data_only=True)
    xl_data = []
    for worksheet in workbook.worksheets:
        rows = worksheet.rows
        if with_header:
            order = []
            for header_cell in next(rows):
                header = header_cell.value
                try:
                    idx = columns.index(header.lower().replace(' ', '_'))
                    order.append(idx)
                except ValueError:
                    return
        else:
            order = range(len(columns))

        for row in rows:
            data = {}
            for i, cell in enumerate(row):
                data[columns[order[i]]] = cell.value
            xl_data.append(data)

    return xl_data
