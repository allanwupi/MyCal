from unittest import TestCase
from datetime import datetime

from app import create_app, db
from app.config import TestConfig
from app.models import User, Friendship, Event, TaskStatus, create_test_data
from app.routes import normalise_email, normalise_username, parse_iso_datetime, merge_busy_intervals


class TestModels(TestCase):
    def setUp(self):
        testApp = create_app(TestConfig)
        self.app_context = testApp.app_context()
        self.app_context.push()
        db.create_all()
        create_test_data()
        return super().setUp()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()
        return super().tearDown()
    
    def test_password_hashing(self):
        user = db.session.get(User, "testuser@example.com")
        user.set_password("you-will-never-guess")
        self.assertTrue(user.check_password("you-will-never-guess"), "Password check returned False for correct password, expected True")
        self.assertFalse(user.check_password("this-is-wrong"), "Password check returned True for incorrect password, expected False")
    
    def test_friendship_to_dict(self):
        friendship = db.session.query(Friendship).first()
        friendship_dict = friendship.to_dict()
        self.assertEqual(friendship_dict.get('id'), friendship.id, "Friendship ID in dict does not match Friendship ID")
        self.assertEqual(friendship_dict.get('requester_email'), friendship.requester_email, "Friendship requester_email in dict does not match Friendship requester_email")
        self.assertEqual(friendship_dict.get('receiver_email'), friendship.receiver_email, "Friendship receiver_email in dict does not match Friendship receiver_email")
        self.assertEqual(friendship_dict.get('status'), friendship.status.value, "Friendship status in dict does not match Friendship status value")
        self.assertEqual(friendship_dict.get('created_at'), friendship.created_at.isoformat(), "Friendship created_at in dict does not match Friendship created_at")
    
    def test_event_to_dict(self):
        event = db.session.query(Event).first()
        event_dict = event.to_dict()
        self.assertEqual(event_dict.get('id'), event.id, "Event ID in dict does not match Event ID")
        self.assertEqual(event_dict.get('title'), event.title, "Event title in dict does not match Event title")
        self.assertEqual(event_dict.get('start'), event.start.isoformat(), "Event start time in dict does not match Event start time")
        self.assertEqual(event_dict.get('end'), event.end.isoformat(), "Event end time in dict does not match Event end time")
        self.assertEqual(event_dict.get('backgroundColor'), event.backgroundColor, "Event background color in dict does not match Event background color")
        self.assertEqual(event_dict.get('durationEditable'), not event.isTask, "Event durationEditable in dict does not match expected value based on isTask")
        self.assertEqual(event_dict.get('extendedProps', {}).get('location'), event.location, "Event location in extendedProps does not match Event location")
        self.assertEqual(event_dict.get('extendedProps', {}).get('description'), event.description, "Event description in extendedProps does not match Event description")
        self.assertEqual(event_dict.get('extendedProps', {}).get('isTask'), event.isTask, "Event isTask in extendedProps does not match Event isTask")
        self.assertEqual(event_dict.get('extendedProps', {}).get('taskStatus'), event.taskStatus.value if event.taskStatus else None, "Event taskStatus in extendedProps does not match Event taskStatus value")
        self.assertEqual(event_dict.get('extendedProps', {}).get('owner'), event.owner, "Event owner in extendedProps does not match Event owner")


class TestHelperFunctions(TestCase):
    def test_normalise_email(self):
        email = "  TEST@EXAMPLE.COM  "
        result = normalise_email(email)
        self.assertEqual(
            result,
            "test@example.com"
        )

    def test_normalise_username(self):
        username = "   Hongshen   "
        result = normalise_username(username)
        self.assertEqual(
            result,
            "Hongshen"
        )

    def test_parse_iso_datetime(self):
        value = "2026-05-14T10:30:00"
        result = parse_iso_datetime(value)
        self.assertEqual(
            result,
            datetime(2026, 5, 14, 10, 30)
        )

    def test_merge_busy_intervals(self):
        intervals = [
            (
                datetime(2026, 5, 14, 10, 0),
                datetime(2026, 5, 14, 11, 0)
            ),
            (
                datetime(2026, 5, 14, 10, 30),
                datetime(2026, 5, 14, 12, 0)
            )
        ]
        result = merge_busy_intervals(intervals)
        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0][0],
            datetime(2026, 5, 14, 10, 0)
        )
        self.assertEqual(
            result[0][1],
            datetime(2026, 5, 14, 12, 0)
        )