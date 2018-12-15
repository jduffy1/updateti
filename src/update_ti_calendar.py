from collections import namedtuple
import datetime
import json
import logging
from logging.handlers import SysLogHandler
import re
import requests

TI_CALENDAR_URL = "http://www.triathlonireland.com/Events/Race-Calendar/"
TI_RACE_ENTRY_URL = "http://www.triathlonireland.com/membership/RaceEntry.aspx?id=%s"
TI_CALENDAR_QUERY = '{"json":"{\\"TypeBySport\\": \\"\\", \\"Distance\\": null, \\"Year\\": null, \\"SwimLocation\\": null, ' \
                    '\\"IsAdult\\": \\"\\"}"}'
RACE_REQUEST_SERVICE = "http://www.triathlonireland.com/webservices/RaceRequestService.asmx/GetActiveRaces"
DEFAULT_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(funcName)s %(message)s')
handler = SysLogHandler(address="/dev/log")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

RaceData = namedtuple('RaceData',
                      ["location", "title", "race_type", "distance", "organiser", "entry_url", "start_time"])


class CalendarDownloader(object):

    @staticmethod
    def get_calendar():
        response = requests.post(RACE_REQUEST_SERVICE, TI_CALENDAR_QUERY, headers=DEFAULT_HEADERS)
        if response.status_code == requests.codes.ok:
            logger.info("Successfully downloaded calendar information")
            json_resp = response.json()["d"]
            stripped_text = re.sub("new Date\((\d+,){5}\d+\)", Utils.convert_to_timestamp,
                                   json_resp.replace("\\\"", "\""))
            return json.loads(stripped_text.encode('utf-8'))["CustomObject"]
        else:
            logger.error("Error downloading calendar from %s. Response code: %s, Body: %s", RACE_REQUEST_SERVICE,
                         response.status_code, response.text)


class Race(RaceData):
    pass


class RaceProcessor(object):

    @staticmethod
    def _create_race(race_json):
        location = ",".join([race_json["Location"], race_json["LocationTown"], race_json["LocationCounty"]])
        title = race_json["Name"].encode('utf-8')
        race_type = race_json["TypeBySport"].encode('utf-8')
        distance = race_json["Distance"].encode('utf-8')
        organiser = race_json["OrganisationOther"].encode('utf-8')
        entry_url = race_json["OrganiserEntryUrl"].encode('utf-8')
        start_time = race_json["RaceDateTime"].encode('utf-8')
        default_entry_url = TI_RACE_ENTRY_URL % race_json["Id"]

        if entry_url == '':
            if requests.get(default_entry_url).status_code == requests.codes.ok:
                entry_url = default_entry_url
            else:
                entry_url = "Link to Entry Website not available"
        return Race(location, title, race_type, distance, organiser, entry_url, start_time)

    @staticmethod
    def process_race_calendar(calendar_json):
        race_list = []
        for race_json in calendar_json:
            race_list.append(RaceProcessor._create_race(race_json))
        return race_list


class Utils(object):

    @staticmethod
    def convert_to_timestamp(date):
        """
        convert from JavaScript Date to timestamp
        Note: month starts at 0 in JS.
        """
        date = re.sub("(new Date\(|\))", "", date.group())
        year, month, day, hours, minutes, seconds = [int(x) for x in date.split(",")]
        month += 1
        return "\"%s\"" % datetime.datetime(year, month, day, hours, minutes, seconds).isoformat()
