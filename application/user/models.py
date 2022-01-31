from flask_login import UserMixin

from application import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String, nullable=False)
    company_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    verified = db.Column(db.Boolean, default=False)
    wells = db.relationship('Well', backref='client', lazy=True)

    @property
    def is_active(self):
        return self.verified


class Well(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_type = db.Column(db.String)
    rig_type = db.Column(db.String)
    location = db.Column(db.String)
    deviation = db.Column(db.String)
    completion_type = db.Column(db.String)
