from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config.from_pyfile('settings.py')
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

from .user import routes
from .admin.routes import admin

app.register_blueprint(admin, url_prefix='/admin')


@app.before_request
def config_request():
    g.flash_map = {
        'success': 'success',
        'error': 'danger',
        'info': 'info'
    }
