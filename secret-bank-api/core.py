import time
import os
import base64
import datetime
import logging
import sys
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
DOWNLOADS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'capitalone')

class GMail:
    def __init__(self):
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        self.service = build('gmail', 'v1', http=creds.authorize(Http()))

    def list_messages(self, min_date):
        results = self.service.users().messages().list(
            userId='me',
            q=f'after:{min_date} from:capitalone@notification.capitalone.com').execute()
        logging.info('Found {} messages'.format(results['resultSizeEstimate']))
        if results['resultSizeEstimate'] > 0:
            return results['messages']
        else:
            return []

    def download_message(self, id, force=False):
        filename = os.path.join(DOWNLOADS, f'{id}.txt')
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
                    time.sleep(2)


if __name__ == '__main__':
    MIN_DATE = (datetime.datetime.now() - datetime.timedelta(10)).strftime('%Y-%m-%d')
    gmail = GMail()
    for message in gmail.list_messages(MIN_DATE):
        gmail.download_message(message['id'])
