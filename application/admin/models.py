from sqlalchemy.inspection import inspect

from application import db, ma
from application.utils import model_to_id, load_marshmallow_schema

__all__ = ['WellCost', 'WellCostSchema', 'WellCostUnit', 'WellCostUnitSchema', 'WellCostCategory',
           'WellCostCategorySchema', 'WellParameters', 'WellParametersSchema', 'RigType', 'RigTypeSchema', 'RigRate',
           'RigRateSchema', 'XmasTree', 'XmasTreeSchema', 'WellHead', 'WellHeadSchema', 'TubingSize', 'TubingSizeSchema']


class ModelBase:
    @classmethod
    def generate_fields(cls, exclude_id=False):
        mapper = inspect(cls)
        rel_names, relationships = mapper.relationships.keys(), mapper.relationships.values()
        fields = []
        for name, column in mapper.columns.items():
            field = {'align': 'center'}
            if name == 'id' and exclude_id:
                continue
            if name == 'id':
                field.update({
                    'width': 50,
                    'readOnly': True
                })
            field['name'] = name
            rel_name = ''

            if hasattr(cls, 'fields_config') and cls.fields_config.get(name):
                config = cls.fields_config[name]
                field.update(config)

            if len(name.split('_')) == 2 and name.split('_')[1] in ['id', 'type'] and name.split('_')[0] in rel_names:
                rel_name = name.split('_')[0]
                relationship = relationships[rel_names.index(name.split('_')[0])]
                _class = relationship.mapper.class_
                Schema = load_marshmallow_schema(_class)
                schema = Schema(many=True)
                field.update({
                    'name': rel_name,
                    'type': 'select',
                    'items': schema.dump(_class.query.all()),
                    'valueField': 'id',
                    'textField': name.split('_')[1] if name.split('_')[1] == 'type' else rel_name
                })
            elif isinstance(column.type, db.Integer):
                field['type'] = 'number'
            elif isinstance(column.type, (db.String, db.Text, db.Float)):
                field['type'] = 'text'
            elif isinstance(column.type, db.Boolean):
                field['type'] = 'checkbox'

            if not field.get('title'):
                field['title'] = name.replace('_', ' ').title() if not rel_name else rel_name.title()

            fields.append(field)

        return fields


'''
    =================
        Well Cost
    =================
'''


class WellCost(db.Model, ModelBase):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer)
    item = db.Column(db.String, nullable=False)
    unit = db.relationship('WellCostUnit', uselist=False, backref='well_cost', lazy=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('well_cost_unit.id'))
    unit_cost = db.Column(db.Float)
    category = db.relationship('WellCostCategory', uselist=False, backref='well_cost', lazy=True)
    category_id = db.Column(db.Integer, db.ForeignKey('well_cost_category.id'))
    operating_time = db.Column(db.Boolean, default=False)

    fields_config = {
        'code': {'width': 80},
        'item': {'title': 'Cost Item', 'width': 150},
    }


class WellCostUnit(db.Model, ModelBase):
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String, nullable=False)


class WellCostCategory(db.Model, ModelBase):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String, nullable=False)


class WellCostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WellCost
        exclude = ('id',)
        include_relationships = True
        load_instance = True


class WellCostUnitSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WellCostUnit
        load_instance = True


class WellCostCategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WellCostCategory
        load_instance = True


'''
    ================
        Job Type
    ================
'''


# class JobType(db.Model, ModelBase):
#     id = db.Column(db.Integer, primary_key=True)
#     type = db.Column(db.String, nullable=False)
#
#
# class JobTypeSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = JobType
#         include_relationships = True
#         load_instance = True


'''
    ================
        Rig Type
    ================
'''


class RigType(db.Model, ModelBase):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False, unique=True)
    rig_up = db.Column(db.Integer)
    depth = db.Column(db.Integer)


class RigTypeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RigType
        load_instance = True


'''
    ================
        Location
    ================
'''


# class Location(db.Model, ModelBase):
#     id = db.Column(db.Integer, primary_key=True)
#     location = db.Column(db.String, nullable=False)
#
#
# class LocationSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Location
#         include_relationships = True
#         load_instance = True


'''
    ======================
        Well Deviation
    ======================
'''


# class WellDeviation(db.Model, ModelBase):
#     id = db.Column(db.Integer, primary_key=True)
#     deviation = db.Column(db.String, nullable=False)
#
#
# class WellDeviationSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = WellDeviation
#         include_relationships = True
#         load_instance = True


'''
    =======================
        Completion Type
    =======================
'''


# class CompletionType(db.Model, ModelBase):
#     id = db.Column(db.Integer, primary_key=True)
#     type = db.Column(db.String, nullable=False)
#
#
# class CompletionTypeSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = CompletionType
#         include_relationships = True
#         load_instance = True


class WellParameters(db.Model, ModelBase):
    id = db.Column(db.Integer, primary_key=True)
    job_type = db.Column(db.String)
    location = db.Column(db.String)
    deviation = db.Column(db.String)
    completion_type = db.Column(db.String)
    perforating_type = db.Column(db.String)
    drilling = db.Column(db.String)
    operation_timeline = db.Column(db.String)


class WellParametersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WellParameters
        include_relationships = True
        load_instance = True


class XmasTree(db.Model, ModelBase):
    id = db.Column(db.Integer, primary_key=True)
    tree_type = db.Column(db.String, nullable=False, unique=True)
    cost = db.Column(db.Float)


class XmasTreeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = XmasTree
        include_relationships = True
        load_instance = True


class WellHead(db.Model, ModelBase):
    id = db.Column(db.Integer, primary_key=True)
    head = db.Column(db.String, nullable=False, unique=True)
    cost = db.Column(db.Float)


class WellHeadSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WellHead
        include_relationships = True
        load_instance = True


class TubingSize(db.Model, ModelBase):
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String, nullable=False, unique=True)
    cost = db.Column(db.Float)


class TubingSizeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TubingSize
        include_relationships = True
        load_instance = True


class RigRate(db.Model, ModelBase):
    rig = db.relationship('RigType', uselist=False, backref='rig_rate', lazy=True)
    rig_type = db.Column(db.String, db.ForeignKey('rig_type.type'), primary_key=True)
    mob = db.Column(db.Integer)
    demob = db.Column(db.Integer)
    day_rate = db.Column(db.Integer)
    solid_control_eqpt = db.Column(db.Float)
    extra_catering = db.Column(db.Integer)
    marine_spread = db.Column(db.Integer)
    additional_marine_spread = db.Column(db.Integer)
    diesel_usage = db.Column(db.Integer)
    water = db.Column(db.Integer)


class RigRateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RigRate
        include_relationships = True
        load_instance = True


model_mapping = {
    'Well Cost': [
        ['Cost', model_to_id(WellCost)],
        ['Unit', model_to_id(WellCostUnit)],
        ['Category', model_to_id(WellCostCategory)]
    ],
    'Rig': [
        ['Rig Type', model_to_id(RigType)],
        ['Rig Rate', model_to_id(RigRate)]
    ],
    'Well Parameters': model_to_id(WellParameters),
    'Xmas Tree': model_to_id(XmasTree),
    'Well Head': model_to_id(WellHead),
    'Tubing Size': model_to_id(TubingSize)
}
