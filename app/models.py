from app import db
from datetime import datetime
import enum
from flask_login import UserMixin
from sqlalchemy import Enum, UniqueConstraint, CheckConstraint
from werkzeug.security import generate_password_hash, check_password_hash


class TaskStatus(enum.Enum):
    NOT_STARTED = 'Not Started'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'


class User(UserMixin, db.Model):
    email = db.Column(db.String(120), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    events = db.relationship('Event', backref='user', lazy=True)

    def get_id(self):
        return self.email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    requester_email = db.Column(
        db.String(120),
        db.ForeignKey(User.email),
        nullable=False
    )

    addressee_email = db.Column(
        db.String(120),
        db.ForeignKey(User.email),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    requester = db.relationship(
        'User',
        foreign_keys=[requester_email],
        backref='sent_friendships'
    )

    addressee = db.relationship(
        'User',
        foreign_keys=[addressee_email],
        backref='received_friendships'
    )

    __table_args__ = (
        UniqueConstraint(
            'requester_email',
            'addressee_email',
            name='unique_friendship'
        ),
        CheckConstraint(
            'requester_email != addressee_email',
            name='no_self_friendship'
        ),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'requester_email': self.requester_email,
            'requester_username': self.requester.username,
            'addressee_email': self.addressee_email,
            'addressee_username': self.addressee.username,
            'created_at': self.created_at.isoformat()
        }


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    backgroundColor = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    isTask = db.Column(db.Boolean, default=False)
    taskStatus = db.Column(Enum(TaskStatus), nullable=True)
    owner = db.Column(db.String(120), db.ForeignKey(User.email), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'backgroundColor': self.backgroundColor,
            'durationEditable': not self.isTask,
            'extendedProps': {
                'location': self.location,
                'description': self.description,
                'isTask': self.isTask,
                'taskStatus': self.taskStatus.value if self.taskStatus else None,
                'owner': self.owner
            }
        }


def create_test_data(owner_email):
    task1 = Event(
        title='Assignment Due',
        start=datetime(2026, 4, 25, 14, 0, 0),
        end=datetime(2026, 4, 25, 14, 0, 0),
        backgroundColor='#6366f1',
        location='UWA Library',
        description='Complete and submit the final assignment.',
        isTask=True,
        taskStatus=TaskStatus.COMPLETED,
        owner=owner_email
    )

    task2 = Event(
        title='Study for Test',
        start=datetime(2026, 4, 20, 9, 0, 0),
        end=datetime(2026, 4, 20, 9, 0, 0),
        backgroundColor='#6366f1',
        location='Home',
        description='Review lecture notes and practice problems.',
        isTask=True,
        taskStatus=TaskStatus.IN_PROGRESS,
        owner=owner_email
    )

    event1 = Event(
        title='Gym Session',
        start=datetime(2026, 4, 22, 16, 0, 0),
        end=datetime(2026, 4, 22, 18, 0, 0),
        backgroundColor='#6366f1',
        location='Campus Gym',
        description='Strength workout and cardio session.',
        owner=owner_email
    )

    event2 = Event(
        title='Group Meeting',
        start=datetime(2026, 4, 23, 10, 0, 0),
        end=datetime(2026, 4, 23, 11, 0, 0),
        backgroundColor='#6366f1',
        location='Engineering Building',
        description='Project discussion with team members.',
        isTask=False,
        owner=owner_email
    )

    db.session.add_all([task1, task2, event1, event2])
    db.session.commit()