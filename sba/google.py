from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from sba.emails import EmailMixin
from sba.sheets import SheetsMixin
from sba import config

# If modifying these scopes, delete the file token.json.
SCOPES = ' '.join([
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/spreadsheets'])

class Google(EmailMixin, SheetsMixin):
    def __init__(self, credentials='credentials.json', token='token.json'):
        store = file.Storage(token)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(credentials, SCOPES)
            creds = tools.run_flow(flow, store)
        self.mail_service = build('gmail', 'v1', http=creds.authorize(Http()))
        self.sheets_service = build('sheets', 'v4', http=creds.authorize(Http()))
        self._transaction_backend_sheet_id = config.transaction_backend_sheet_id()
