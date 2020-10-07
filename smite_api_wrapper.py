import requests
from datetime import datetime
import hashlib
import json
from typing import List

base_url = "http://api.smitegame.com/smiteapi.svc/"
devId = 'YOUR DEV ID'
authKey = 'YOUR AUTH KEY'
response_frmt = 'Json'


class SmiteAPI:

    def __init__(self, dev_id: str, auth_key: str):
        """Session is not created until a request is made"""
        self.dev_id = dev_id
        self.auth_key = auth_key
        self.base_url = base_url
        self.session_id = None
        self.lang_code = '1'

    def _create_timestamp(self) -> str:
        """Creates the current timestamp formatted properly"""
        current_datetime = datetime.utcnow()
        return current_datetime.strftime("%Y%m%d%H%M%S")

    def _create_signature(self, methodname: str) -> str:
        """Returns str of encoded signature"""
        timestamp = self._create_timestamp()
        return hashlib.md5(self.dev_id.encode('utf-8') + methodname.encode('utf-8') +
                           self.auth_key.encode('utf-8') + timestamp.encode('utf-8')).hexdigest()

    def create_session(self):
        """Creates and Updates the session, and self.session.id"""
        sig = self._create_signature('createsession')
        url = f'{self.base_url}/createsessionJson/{self.dev_id}/{sig}/{self._create_timestamp()}'
        req = requests.get(url).json()
        self.session_id = req['session_id']

    def test_session(self) -> True:
        """Checks if there is a current valid session, if not it creates one"""
        if self.session_id is None:
            self.create_session()
            return True
        else:
            url = f"{base_url}testsession{response_frmt}/{self.dev_id}/" \
                  f"{self._create_signature('testsession')}/{self.session_id}/{self._create_timestamp()}"
            req = requests.get(url)
            if 'successful' in req.text:
                return True
            else:
                self.create_session()
                print('Restarting session')
                return True

    def create_request(self, methodname: str, params=None):
        """Takes the method and parameters which are then built into a url and requested, returns json"""
        if self.test_session():
            url = self.create_url(methodname, params)
            print(url)
            req = requests.get(url)
            return json.loads(req.text, encoding='utf-8')
        else:
            self.create_session()

    def create_url(self, methodname, params=()) -> str:
        """Builds and returns the url to be requested when given the parameters and methodname"""
        signature = self._create_signature(methodname)
        timestamp = self._create_timestamp()
        partial_url = [methodname + response_frmt, self.dev_id, signature, self.session_id, timestamp]
        if params:
            for param in params:
                if type(param) == list:
                    partial_url.append(str(param[0]))
                else:
                    partial_url.append(str(param))
        return base_url + '/'.join(partial_url)

    def get_gods(self) -> list:
        """Return Json of every God and their stats"""
        data = self.create_request('getgods', [self.lang_code])
        return data

    def get_player(self, player_name: List[str]) -> list:
        """Return Json of a requested player by name"""
        data = self.create_request('getplayer', player_name)
        return data

    def get_god_skins(self, god_id: List[str]):
        """Return Json of all skins for particular god by ID"""
        data = self.create_request('getgodskins', [god_id, [self.lang_code]])
        return data

    def get_god_leaderboard(self, god_id: List[str], queue: List[str]) -> list:
        """Return Json leaderboard data for a specific god and queue"""
        data = self.create_request('getgodleaderboard', [god_id, queue])
        return data

    def get_god_recommended_items(self, god_id: List[str]) -> list:
        """Return recommended items for a particular god by ID"""
        data = self.create_request('getgodrecommendeditems', [god_id, self.lang_code])
        return data

    def get_items(self) -> list:
        """Return all items in Smite"""
        data = self.create_request('getitems', [self.lang_code])
        return data
