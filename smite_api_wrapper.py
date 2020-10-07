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

    def _create_session(self):
        """Creates and Updates the session, and self.session.id"""
        sig = self._create_signature('createsession')
        url = f'{self.base_url}/createsessionJson/{self.dev_id}/{sig}/{self._create_timestamp()}'
        req = requests.get(url).json()
        self.session_id = req['session_id']

    def _test_session(self) -> True:
        """Checks if there is a current valid session, if not it creates one"""
        if self.session_id is None:
            self._create_session()
            return True
        else:
            url = f"{base_url}testsession{response_frmt}/{self.dev_id}/" \
                  f"{self._create_signature('testsession')}/{self.session_id}/{self._create_timestamp()}"
            req = requests.get(url)
            if 'successful' in req.text:
                return True
            else:
                self._create_session()
                print('Restarting session')
                return True

    def _create_request(self, methodname: str, params=None):
        """Takes the method and parameters which are then built into a url and requested, returns json"""
        if self._test_session():
            url = self._create_url(methodname, params)
            print(url)
            req = requests.get(url)
            return json.loads(req.text, encoding='utf-8')
        else:
            self._create_session()

    def _create_url(self, methodname, params=()) -> str:
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

    def get_patch_info(self) -> dict:
        """Function returns information about current deployed patch.
         Currently, this information only includes patch version"""
        data = self._create_request('getpatchinfo')
        return data

    def get_gods(self) -> list:
        """Returns all Gods and their various attributes"""
        data = self._create_request('getgods', [self.lang_code])
        return data

    def get_god_skins(self, god_id: List[str]) -> list:
        """Returns all available skins for a particular God"""
        data = self._create_request('getgodskins', [god_id, self.lang_code])
        return data

    def get_god_leaderboard(self, god_id: List[str], queue: List[str]) -> list:
        """Returns the current season’s leaderboard for a god/queue combination"""
        data = self._create_request('getgodleaderboard', [god_id, queue])
        return data

    def get_god_recommended_items(self, god_id: List[str]) -> list:
        """Returns the Recommended Items for a particular God"""
        data = self._create_request('getgodrecommendeditems', [god_id, self.lang_code])
        return data

    def get_items(self) -> list:
        """Returns all Items and their various attributes"""
        data = self._create_request('getitems', [self.lang_code])
        return data

    def get_player(self, player_name: List[str]) -> list:
        """Returns league and other high level data for a particular player"""
        data = self._create_request('getplayer', [player_name])
        return data

    def get_player_id(self, player_name: List[str]) -> list:
        """Returns a player id, which is used for other function calls"""
        data = self._create_request('getplayeridbyname', [player_name])
        try:
            return [data[0]['player_id']]
        except KeyError:
            print('Player not found')

    def get_friends(self, player_id: list) -> list:
        """Returns the Smite User names of each of the player’s friends. [PC only]"""
        data = self._create_request('getfriends', [player_id])
        return data

    def get_god_ranks(self, player_id: list) -> list:
        """Returns the Rank and Worshippers value for each God a player has played"""
        data = self._create_request('getgodranks', [player_id])
        return data

    def get_player_achievements(self, player_id: list) -> dict:
        """Returns select achievement totals for the specified playerId"""
        data = self._create_request('getplayerachievements', [player_id])
        return data

    def get_player_status(self, player_id: list) -> list:
        """Returns players current online status"""
        data = self._create_request('getplayerstatus', [player_id])
        return data

    def get_match_history(self, player_id: list) -> list:
        """Gets recent matches and high level match statistics for a particular player"""
        data = self._create_request('getmatchhistory', [player_id])
        return data
