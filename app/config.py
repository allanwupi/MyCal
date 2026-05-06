import os

basedir = os.path.abspath(os.path.dirname(__file__))
default_db_path = 'sqlite:///' + os.path.join(basedir, 'mycal.db')

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYCAL_DATABASE_URL') or default_db_path
    SECRET_KEY = os.environ.get('MYCAL_SECRET_KEY') or 'dev-secret-key-change-before-deployment'
    SQLALCHEMY_TRACK_MODIFICATIONS = False