from app import db
from datetime import datetime
import enum
from sqlalchemy import Enum


class TaskStatus(enum.Enum):
    NOT_STARTED = 'Not Started'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'


class User(db.Model):
    email = db.Column(db.String(120), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start = db.Column(db.DateTime, nullable=False)  # For tasks, treat the start datetime as the due date and time
    end = db.Column(db.DateTime, nullable=False)
    backgroundColor = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    isTask = db.Column(db.Boolean, default=False)
    taskStatus = db.Column(Enum(TaskStatus), nullable=True)
    owner = db.Column(db.String(120), db.ForeignKey(User.email), nullable=True)  # For future user association

    def to_dict(self): # Converts event object to a dictionary for JSON serialization
        return {
            'id': self.id,
            'title': self.title,
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'backgroundColor': self.backgroundColor,
            'extendedProps': {
                'location': self.location,
                'description': self.description,
                'isTask': self.isTask,
                'taskStatus': self.taskStatus.value if self.taskStatus else None,
                'owner': self.owner
            }
        }


def create_test_data():
    task1 = Event(
        id=1,
        title='Assignment Due',
        start=datetime(2026, 4, 25, 14, 0, 0),
        end=datetime(2026, 4, 25, 14, 0, 0),
        backgroundColor='#6366f1',
        location='UWA Library',
        description='Complete and submit the final assignment.',
        isTask=True,
        taskStatus=TaskStatus.COMPLETED
    )
    task2 = Event(
        id=2,
        title='Study for Test',
        start=datetime(2026, 4, 20, 9, 0, 0),
        end=datetime(2026, 4, 20, 9, 0, 0),
        backgroundColor='#6366f1',
        location='Home',
        description='Review lecture notes and practice problems.',
        isTask=True,
        taskStatus=TaskStatus.IN_PROGRESS
    )
    event1 = Event(
        id=3,
        title='Gym Session',
        start=datetime(2026, 4, 22, 16, 0, 0),
        end=datetime(2026, 4, 22, 18, 0, 0),
        backgroundColor='#6366f1',
        location='Campus Gym',
        description='Strength workout and cardio session.'
    )
    event2 = Event(
        id=4,
        title='Group Meeting',
        start=datetime(2026, 4, 23, 10, 0, 0),
        end=datetime(2026, 4, 23, 11, 0, 0),
        backgroundColor='#6366f1',
        location='Engineering Building',
        description='Project discussion with team members.',
        isTask=False
    )
    events = [task1, task2, event1, event2]
    db.session.add_all(events)
    db.session.commit()