import requests
from datetime import datetime
import hashlib
import json

base_url = "http://api.smitegame.com/smiteapi.svc/"
devId = 'YOUR DEV ID'
authKey = 'YOUR AUTH KEY'
response_frmt = 'Json'


class SmiteAPI:

    def __init__(self, dev_id, auth_key):
        self.dev_id = dev_id
        self.auth_key = auth_key
        self.base_url = base_url
        self.session_id = None

    def _create_timestamp(self):
        datime_now = datetime.utcnow()
        return datime_now.strftime("%Y%m%d%H%M%S")

    def _create_signature(self, methodname):
        timestamp = self._create_timestamp()
        return hashlib.md5(self.dev_id.encode('utf-8') + methodname.encode('utf-8') +
                           self.auth_key.encode('utf-8') + timestamp.encode('utf-8')).hexdigest()

    def create_session(self):
        sig = self._create_signature('createsession')
        url = f'{self.base_url}/createsessionJson/{devId}/{sig}/{self._create_timestamp()}'
        req = requests.get(url).json()
        self.session_id = req['session_id']

    def test_session(self):
        if self.session_id == None:
            print('Invalid Session. Session not created.')
        else:
            url = f"{base_url}testsession{response_frmt}/{self.dev_id}/" \
                  f"{self._create_signature('testsession')}/{self.session_id}/{self._create_timestamp()}"
            req = requests.get(url)
            if 'successful' in req.text:
                print('session is valid!')
                return True
            else:
                self.create_session()
                print('invalid session')
                return False

    def create_request(self, methodname, params=None):
        if self.test_session():
            url = self.create_url(methodname, params)
            print(url)
            req = requests.get(url)
            return json.loads(req.text, encoding='utf-8')
        else:
            self.create_session()

    def create_url(self, methodname, params=()):
        signature = self._create_signature(methodname)
        timestamp = self._create_timestamp()
        partial_url = [methodname + response_frmt, self.dev_id, signature, self.session_id, timestamp]
        if params:
            for param in params:
                partial_url.append(str(param))
        return base_url + '/'.join(partial_url) + '/1'

    def get_gods(self):
        self.create_session()
        data = self.create_request('getgods')
        return data

    def get_player(self, player_name):
        self.create_session()
        data = self.create_request('getplayer', player_name)
        return data
