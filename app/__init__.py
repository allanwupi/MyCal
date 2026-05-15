from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'landing'
login_manager.login_message = 'Please log in to access your dashboard.'
login_manager.login_message_category = 'warning'

from app.models import User


@login_manager.user_loader
def load_user(email):
    return User.query.get(email)


from app import routes, models


@app.cli.command('init-db')
def init_db_command():
    """Create database tables for local development."""
    db.create_all()
    print('Database tables created.')


@app.cli.command('clear-db')
def clear_db_command():
    """Clear all data from the database tables for local development."""
    db.drop_all()
    db.create_all()
    print('Database tables cleared and recreated.')