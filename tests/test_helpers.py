import unittest
from datetime import datetime

from app.routes import (
    normalise_email,
    normalise_username,
    parse_iso_datetime,
    merge_busy_intervals
)


class HelperFunctionTest(unittest.TestCase):

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


if __name__ == "__main__":
    unittest.main()