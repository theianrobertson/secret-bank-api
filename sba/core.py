import time
import os
import base64
import datetime
import logging
import sys

import yaml
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

CURR_DIR = os.path.abspath(os.path.dirname(__file__))
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
DOWNLOADS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'capitalone')

class GMail:
    def __init__(self, credentials='credentials.json', token='token.json'):
        store = file.Storage(token)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(credentials, SCOPES)
            creds = tools.run_flow(flow, store)
        self.service = build('gmail', 'v1', http=creds.authorize(Http()))

    def list_messages(self, base_search, min_date=None):
        if min_date:
            base_search = base_search + f" after:{min_date}"
        results = self.service.users().messages().list(
            userId='me',
            q=base_search).execute()
        logging.info('Found {} messages'.format(results['resultSizeEstimate']))
        if results['resultSizeEstimate'] > 0:
            return results['messages']
        else:
            return []

    def download_message(self, id, force=False, directory=None, sleep_time=2):
        """Download a message based on an ID

        Parameters
        ----------
        id : str
            The message ID from GMail
        force : bool, optional
            Whether to force the download.  If False and the file already exists in the directory,
            don't re-download.
        directory : str, optional
            Optional directory to use.  Defaults to current working directory.
        sleep_time : int, optional
            Seconds to sleep after pulling the email (to be a good citizen)
        """
        directory = directory or os.getcwd()
        filename = os.path.join(directory, f'{id}.txt')
        if force or not(os.path.isfile(filename)):
            results = self.service.users().messages().get(
                userId='me',
                id=id).execute()
            part = [part for part in results['payload']['parts'] if part['mimeType'] == 'text/plain'][0]
            if part:
                text = part['body']['data']
                decoded_bytes = base64.urlsafe_b64decode(text)
                fully_decoded = decoded_bytes.decode('utf-8')
                with open(filename, 'w') as file_open:
                    file_open.write(fully_decoded)
                    logging.info('Wrote out message ID {}'.format(id))
                    time.sleep(sleep_time)

    def catch_em_all(self, days=7, directory=None):
        """Grabs all emails that match searchers in the past few days

        Parameters
        ----------
        days : int, optional
            Number of days to reach into the past
        directory : str, optional
            Defaults to current working directory, this is the base directory.
        """
        directory = directory or os.getcwd()
        min_date = (datetime.datetime.now() - datetime.timedelta(days)).strftime('%Y-%m-%d')
        searchers = get_searchers()
        for institution, alerts in searchers.items():
            for alert_type, base_search in alerts.items():
                logging.info('Grabbing {} {} alerts'.format(institution, alert_type))
                download_dir = os.path.join(directory, institution, alert_type)
                os.makedirs(download_dir, exist_ok=True)
                for message in self.list_messages(base_search, min_date=min_date):
                    self.download_message(message['id'], directory=download_dir)


def get_searchers():
    with open(os.path.join(CURR_DIR, 'searchers.yaml'), encoding="utf-8") as file_open:
        return yaml.load(file_open)
