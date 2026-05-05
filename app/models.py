from app import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    backgroundColor = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    isTask = db.Column(db.Boolean, default=False)
    taskStatus = db.Column(db.String(20), nullable=True)  # 'Not Started', 'In Progress', 'Completed'
    owner = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)  # For future user association

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
                'taskStatus': self.taskStatus,
                'owner': self.owner
            }
        }


def create_test_data():
    event1 = Event(
        id=1,
        title='Assignment Due',
        start=datetime(2026, 4, 25, 14, 0, 0),
        end=datetime(2026, 4, 25, 16, 0, 0),
        backgroundColor='#6366f1',
        location='UWA Library',
        description='Complete and submit the final assignment.',
        isTask=True,
        taskStatus='Completed'
    )
    event2 = Event(
        id=2,
        title='Group Meeting',
        start=datetime(2026, 4, 23, 10, 0, 0),
        end=datetime(2026, 4, 23, 11, 0, 0),
        backgroundColor='#3b82f6',
        location='Engineering Building',
        description='Project discussion with team members.',
        isTask=False
    )
    event3 = Event(
        id=3,
        title='Gym Session',
        start=datetime(2026, 4, 22, 18, 0, 0),
        end=datetime(2026, 4, 22, 19, 30, 0),
        backgroundColor='#8b5cf6',
        location='Campus Gym',
        description='Strength workout and cardio session.',
        isTask=False
    )
    events = [event1, event2, event3]
    db.session.add_all(events)
    db.session.commit()