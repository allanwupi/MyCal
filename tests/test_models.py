import unittest
from datetime import datetime

from app import app, db
from app.config import TestConfig
from app.models import User, Event, TaskStatus

class UserModelTest(unittest.TestCase):

    def setUp(self):
        app.config.from_object(TestConfig)

        self.app_context = app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")

        self.assertTrue(user.check_password("password123"))
        self.assertFalse(user.check_password("wrongpassword"))

    def test_get_id_returns_email(self):
        user = User(
            username="hongshen",
            email="hongshen@test.com"
        )

        self.assertEqual(user.get_id(), "hongshen@test.com")

    ## test Event.to_dict()， test the function that event can tranform into “” form
    def test_event_to_dict_for_task(self):
        event = Event(
            id=1,
            title="Study for CITS3403",
            start=datetime(2026, 5, 14, 10, 0),
            end=datetime(2026, 5, 14, 10, 0),
            backgroundColor="#6366f1",
            location="Library",
            description="Testing revision",
            isTask=True,
            taskStatus=TaskStatus.IN_PROGRESS,
            owner="hongshen@test.com"
        )

        data = event.to_dict()

        self.assertEqual(data["title"], "Study for CITS3403")
        self.assertEqual(data["extendedProps"]["isTask"], True)
        self.assertEqual(data["extendedProps"]["taskStatus"], "In Progress")
        self.assertEqual(data["extendedProps"]["owner"], "hongshen@test.com")
        self.assertFalse(data["durationEditable"])


if __name__ == "__main__":
    unittest.main()