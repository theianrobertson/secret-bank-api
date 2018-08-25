import os
import logging
import sys

import yaml
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from sba.emails import EmailMixin
from sba.sheets import SheetsMixin

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

CURR_DIR = os.path.abspath(os.path.dirname(__file__))
# If modifying these scopes, delete the file token.json.
SCOPES = ' '.join([
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/spreadsheets'])
DOWNLOADS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'capitalone')

class Google(EmailMixin, SheetsMixin):
    def __init__(self, credentials='credentials.json', token='token.json', config='config.yml'):
        store = file.Storage(token)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(credentials, SCOPES)
            creds = tools.run_flow(flow, store)
        self.mail_service = build('gmail', 'v1', http=creds.authorize(Http()))
        self.sheets_service = build('sheets', 'v4', http=creds.authorize(Http()))
        self._transaction_backend_sheet_id = get_config(config)['transaction_backend_sheet_id']

def get_searchers():
    with open(os.path.join(CURR_DIR, 'searchers.yaml'), encoding="utf-8") as file_open:
        return yaml.load(file_open)

def get_config(config):
    with open(config, encoding="utf-8") as file_open:
        return yaml.load(file_open)
