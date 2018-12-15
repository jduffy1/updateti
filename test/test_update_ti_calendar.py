import copy
import json
import unittest
from mock import patch, Mock
from update_ti_calendar import CalendarDownloader, RaceProcessor, Race, TI_RACE_ENTRY_URL


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


class TestRaceProcessor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('test_data/single_race.json') as race_file:
            cls.race = json.load(race_file)

    def test_process_race_calendar(self):
        race_list = RaceProcessor.process_race_calendar(self.race)
        self.assertEquals(len(race_list), 1)
        self.assertTrue(isinstance(race_list[0], Race))

    @patch('requests.get', autospec=True)
    def test_process_race_calendar_empty_entry_url(self, mock_get):
        get_response = mock_get.return_value
        get_response.status_code = 200
        race_json = copy.deepcopy(self.race)
        race_json[0]["OrganiserEntryUrl"] = u""
        race_list = RaceProcessor.process_race_calendar(race_json)
        self.assertEquals(race_list[0].entry_url, TI_RACE_ENTRY_URL % race_json[0]["Id"])

    @patch('requests.get', autospec=True)
    def process_race_calendar_empty_entry_url_no_default_url(self, mock_get):
        get_response = mock_get.return_value
        get_response.status_code = 404
        race_json = self.race
        race_json[0]["OrganiserEntryUrl"] = u""
        race_list = RaceProcessor.process_race_calendar(race_json)
        self.assertEquals(race_list[0].entry_url, "Link to Entry Website not available")
