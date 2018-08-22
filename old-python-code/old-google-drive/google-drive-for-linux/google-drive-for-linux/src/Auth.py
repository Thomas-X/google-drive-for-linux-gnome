from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from src.constants import pprint
from src.statics import JSONData

##
## TODO Find out how to safely do auth without shipping application secrets..
##

class Auth:
    def __init__(self):
        self.scope = 'https://www.googleapis.com/auth/drive'
        self.store = file.Storage('json_data/token.json')
        self.creds = self.store.get()
        if not self.creds or self.creds.invalid:
            self.runLoginFlow()
        JSONData.token = self.creds.access_token
        Auth.service = build('drive', 'v2', http=self.creds.authorize(Http()))

    def runLoginFlow(self):
        flow = client.flow_from_clientsecrets('json_data/credentials.json', self.scope)
        self.creds = tools.run_flow(flow, self.store)