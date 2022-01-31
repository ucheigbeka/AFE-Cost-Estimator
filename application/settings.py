from os import environ
from dotenv import load_dotenv

load_dotenv('.env')

SECRET_KEY = environ.get('SECRET_KEY')
SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = bool(environ.get('SQLALCHEMY_TRACK_MODIFICATIONS'))

MAIL_SERVER = environ.get('MAIL_SERVER')
MAIL_PORT = int(environ.get('MAIL_PORT'))
MAIL_USE_SSL = bool(environ.get('MAIL_USE_SSL'))
MAIL_USERNAME = environ.get('MAIL_USERNAME')
MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = environ.get('MAIL_DEFAULT_SENDER')
