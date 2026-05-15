import os

basedir = os.path.abspath(os.path.dirname(__file__))
default_db_path = 'sqlite:///' + os.path.join(basedir, 'mycal.db')

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('MYCAL_SECRET_KEY')
    if SECRET_KEY is None:
        raise ValueError("MYCAL_SECRET_KEY environment variable not set.\nRun 'export MYCAL_SECRET_KEY=<your_secret_key>' starting the application.")

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True

class DeploymentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', default_db_path)