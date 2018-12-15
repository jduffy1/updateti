import logging
import os
import sys
from google.oauth2 import service_account
from googleapiclient import discovery

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'service_auth.json'
TI_CALENDAR = os.environ['TI_CALENDAR']

if __name__ == '__main__':
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    calserv = discovery.build('calendar', 'v3', credentials=credentials,cache_discovery=False)
    races = calserv.events().list(calendarId=TI_CALENDAR).execute()['items']
    logger.info("Found %d races", len(races))
