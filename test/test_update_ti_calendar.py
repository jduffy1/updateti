import json
import unittest 
from mock import patch, Mock
from update_ti_calendar import CalendarDownloader


class TestCalendarDownloader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('test_data/ti_calendar_response.json') as response_file:
            cls.response_data = json.loads("".join(response_file.readlines()))

    @patch('requests.post', autospec=True)
    def test_get_calendar(self, post_mock):
        post_response = post_mock.return_value
        post_response.status_code = 200
        post_response.json = Mock(return_value=self.response_data)
        CalendarDownloader.get_calendar()

    @patch('requests.post', autospec=True)
    def test_get_calendar_returns_none_when_request_fails(self, post_mock):
        post_response = post_mock.return_value
        post_response.status_code = 404
        self.assertIsNone(CalendarDownloader.get_calendar())

    @patch('requests.post', autospec=True)
    def test_get_calendar_raise_ValueError_with_invalid_JSON(self, post_mock):
        post_response = post_mock.return_value
        post_response.status_code = 200
        post_response.json = Mock(return_value={"d": "{a"})
        self.assertRaises(ValueError, CalendarDownloader.get_calendar)
