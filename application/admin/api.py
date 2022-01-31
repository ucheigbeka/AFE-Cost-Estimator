from flask import Blueprint, request

from application import db
from application.utils import id_to_model, load_marshmallow_schema, get_table_columns, parse_xl
from .models import *

api = Blueprint('admin_api', __name__)


def handle_request():
    _id = request.base_url[request.base_url.rfind('/') + 1:]
    Model = id_to_model(_id)
    Schema = load_marshmallow_schema(Model)
    if request.method == 'GET':
        models = Model.query.all()
        schema = Schema(many=True)
        return schema.dumps(models)
    elif request.method in ['POST', 'PUT']:
        schema = Schema()
        model = schema.load(request.form)
        db.session.add(model)
        db.session.commit()
        return schema.dump(model)
    else:
        schema = Schema()
        model = schema.load(request.form)
        db.session.delete(model)
        db.session.commit()
        return dict(request.form)


@api.route('/well-cost', methods=['GET', 'POST', 'PUT', 'DELETE'])
def well_cost():
    if request.method == 'POST':
        well_cost_schema = WellCostSchema()
        cost_dict = dict(request.form)
        cost = well_cost_schema.load(cost_dict)
        db.session.add(cost)
        db.session.commit()
        return well_cost_schema.dump(cost), 200
    elif request.method == 'PUT':
        well_cost_schema = WellCostSchema()
        cost_dict = dict(request.form)
        cost = WellCost.query.filter_by(code=cost_dict['code']).first()
        for key, val in cost_dict.items():
            if key == 'unit':
                cost.unit = WellCostUnit.query.get(val)
            elif key == 'category':
                cost.category = WellCostCategory.query.get(val)
            else:
                setattr(cost, key, val)
        db.session.add(cost)
        db.session.commit()
        return well_cost_schema.dump(cost), 200

    return handle_request(), 200


@api.route('/well-cost-unit', methods=['GET', 'POST', 'PUT', 'DELETE'])
def well_cost_unit():
    return handle_request(), 200


@api.route('/well-cost-category', methods=['GET', 'POST', 'PUT', 'DELETE'])
def well_cost_category():
    return handle_request(), 200


@api.route('/rig-type', methods=['GET', 'POST', 'PUT', 'DELETE'])
def rig_type():
    return handle_request(), 200


@api.route('/rig-rate', methods=['GET', 'POST', 'PUT', 'DELETE'])
def rig_rate():
    if request.method in ['POST', 'PUT']:
        schema = RigRateSchema()
        rate = schema.load(request.form)
        rate.rig = RigRate.query.get(rate.rig)
        db.session.add(rate)
        db.session.commit()
        return schema.dump(rate), 200

    return handle_request(), 200


@api.route('/well-parameters', methods=['GET', 'POST', 'PUT', 'DELETE'])
def well_parameters():
    return handle_request(), 200


@api.route('/xmas-tree', methods=['GET', 'POST', 'PUT', 'DELETE'])
def xmas_tree():
    return handle_request(), 200


@api.route('/well-head', methods=['GET', 'POST', 'PUT', 'DELETE'])
def well_head():
    return handle_request(), 200


@api.route('/tubing-size', methods=['GET', 'POST', 'PUT', 'DELETE'])
def tubing_size():
    return handle_request(), 200


@api.route('/upload-record', methods=['POST'])
def upload_record():
    _id, fd = request.form['activeView'], request.files['fileInput']
    Model = id_to_model(_id)
    Schema = load_marshmallow_schema(Model)
    columns = get_table_columns(model=Model, schema=Schema)
    if 'id' in columns:
        columns.remove('id')
    xl_data = parse_xl(fd, columns)
    if not xl_data:
        return 'Error parsing record.\nColumns don\'t match', 400
    schema = None
    if Schema:
        schema = Schema()
    for data in xl_data:
        if _id == 'well-cost':
            if data['unit']:
                unit = WellCostUnit.query.filter_by(unit=data['unit']).first()
                if not unit:
                    unit = WellCostUnit(unit=data['unit'])
                    db.session.add(unit)
                    db.session.commit()
                data['unit'] = unit.id
            if data['category']:
                category = WellCostCategory.query.filter_by(category=data['category']).first()
                if not category:
                    category = WellCostCategory(category=data['category'])
                    db.session.add(category)
                    db.session.commit()
                data['category'] = category.id
            data['operating_time'] = True if data['operating_time'] == 'OT' else False
        if schema:
            model = schema.load(data)
        else:
            model = Model(**data)
        db.session.add(model)
        db.session.commit()

    return 'Success', 200
