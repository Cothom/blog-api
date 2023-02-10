from datetime import datetime
from unittest import TestCase

from app.utils import datetime_to_iso_string, iso_string_to_datetime


class TestIsoStringToDatetime(TestCase):
    def setUp(self) -> None:
        self.now_str = "2023-02-10T16:34:17.942779"
        self.now = datetime(2023, 2, 10, 16, 34, 17, 942779)
        return super().setUp()

    def test_with_valid_string(self):
        input = self.now_str
        expected = self.now
        output = iso_string_to_datetime(input)
        self.assertEqual(expected, output)

    def test_returns_now_on_empty_string(self):
        input = ""
        before = datetime.now()
        output = iso_string_to_datetime(input)
        after = datetime.now()
        self.assertTrue(before <= output <= after)

    def test_returns_now_on_invalid_string(self):
        input = "20202-10T16:34:17.942779"
        before = datetime.now()
        output = iso_string_to_datetime(input)
        after = datetime.now()
        self.assertTrue(before <= output <= after)


class TestDatetimeToIsoString(TestCase):
    def setUp(self) -> None:
        self.now_str = "2023-02-10T16:34:17.942779"
        self.now = datetime(2023, 2, 10, 16, 34, 17, 942779)
        return super().setUp()

    def test_with_valid_date(self):
        input = self.now
        expected = self.now_str
        output = datetime_to_iso_string(input)
        self.assertEqual(expected, output)
