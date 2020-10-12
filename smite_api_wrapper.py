import requests
from datetime import datetime
import hashlib
import json
from typing import List

devId = 'YOUR DEV ID'
authKey = 'YOUR AUTH KEY'


class HiRezAPI:
    """Class containing session generation, and shared endpoint functions"""
    response_frmt = 'Json'

    @staticmethod
    def _create_timestamp() -> str:
        """Returns the current timestamp formatted properly"""
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
            url = f"{self.base_url}testsession{HiRezAPI.response_frmt}/{self.dev_id}/" \
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
        partial_url = [methodname + HiRezAPI.response_frmt, self.dev_id, signature, self.session_id, timestamp]
        if params:
            for param in params:
                if type(param) == list:
                    partial_url.append(str(param[0]))
                else:
                    partial_url.append(str(param))
        return self.base_url + '/'.join(partial_url)

    def ping(self) -> str:
        """A quick way of validating access to the Hi-Rez API"""
        data = requests.get(f'{self.base_url}/ping{HiRezAPI.response_frmt}')
        return data.text

    def get_data_used(self) -> list:
        """Returns API Developer daily usage limits and the current status against those limits"""
        data = self._create_request('getdataused')
        return data

    def get_server_status(self) -> list:
        """Function returns UP/DOWN status for the primary game/platform environments
          Data is cached once a minute"""
        data = self._create_request('gethirezserverstatus')
        return data

    def get_patch_info(self) -> dict:
        """Function returns information about current deployed patch.
         Currently, this information only includes patch version"""
        data = self._create_request('getpatchinfo')
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

    def search_players(self, player_name: List[str]) -> list:
        """Returns player_id values for all names and/or gamer_tags containing the “searchPlayer” string"""
        data = self._create_request('searchplayers', [player_name])
        return data

    def get_friends(self, player_id: List[str]) -> list:
        """Returns the Smite User names of each of the player’s friends. [PC only]"""
        data = self._create_request('getfriends', [player_id])
        return data

    def get_player_status(self, player_id: List[str]) -> list:
        """Returns players current online status"""
        data = self._create_request('getplayerstatus', [player_id])
        return data

    def get_match_history(self, player_id: List[str]) -> list:
        """Gets recent matches and high level match statistics for a particular player"""
        data = self._create_request('getmatchhistory', [player_id])
        return data

    def get_matchids_by_queue(self, queue: List[str], date: List[str], hour: List[str]) -> list:
        """Lists all Match IDs for a particular Match Queue"""
        data = self._create_request('getmatchidsbyqueue', [queue, date, hour])
        return data

    def get_match_details(self, match_id: List[str]) -> list:
        """Returns the statistics for a particular completed match"""
        data = self._create_request('getmatchdetails', [match_id])
        return data

    def get_queue_stats(self, player_id: List[str], queue: List[str]) -> list:
        """Returns match summary statistics for a (player, queue) combination grouped by gods played"""
        data = self._create_request('getqueuestats', [player_id, queue])
        return data

    def get_top_matches(self):
        """Lists the 50 most watched / most recent recorded matches"""
        data = self._create_request('gettopmatches')
        return data

    def get_league_seasons(self, queue: List[str]) -> list:
        """Provides a list of seasons and rounds (including the single active season) for a match queue"""
        data = self._create_request('getleagueseasons', [queue])
        return data

    def get_league_leaderboard(self, queue: List[str], tier: List[str], round: List[str]) -> list:
        """Returns the top players for a particular league (as indicated by the queue/tier/round parameters).
        Note: the “Season” for which the Round is associated is by default the current/active Season"""
        data = self._create_request('getleagueleaderboard', [queue, tier, round])
        return data

    def get_team_details(self, clan_id: List[str]) -> list:
        """Lists the number of players and other high level details for a particular clan"""
        data = self._create_request('getteamdetails', [clan_id])
        return data

    def get_team_players(self, clan_id: List[str]) -> list:
        """Lists the players for a particular clan"""
        data = self._create_request('getteamplayers', [clan_id])
        return data

    def get_esports_proleague_details(self) -> list:
        """Returns the matchup information for each matchup for the current eSports Pro League season."""
        data = self._create_request('getesportsproleaguedetails')
        return data


class PaladinsAPI(HiRezAPI):
    base_url = 'http://api.paladins.com/paladinsapi.svc/'

    def __init__(self, dev_id: str, auth_key: str):
        """Session is not created until a request is made"""
        self.dev_id = dev_id
        self.auth_key = auth_key
        self.base_url = PaladinsAPI.base_url
        self.session_id = None
        self.lang_code = '1'

    def get_champions(self) -> list:
        """Returns all Champions and their various attributes"""
        data = self._create_request('getchampions', [self.lang_code])
        return data

    def get_champion_cards(self, champion_id: List[str]) -> list:
        """Returns all Champion cards"""
        data = self._create_request('getchampioncards', [champion_id, self.lang_code])
        return data

    def get_champion_leaderboard(self, champion_id: List[str], queue: List[str]) -> list:
        """Returns the current season’s leaderboard for a champion/queue combination"""
        data = self._create_request('getchampionleaderboard', [champion_id, queue])
        return data

    def get_champion_skins(self, champion_id: List[str]) -> list:
        """Returns all available skins for a particular Champion"""
        data = self._create_request('getchampionskins', [champion_id, self.lang_code])
        return data

    def get_champion_ranks(self, player_id: List[str]) -> list:
        """Returns the Rank and Worshippers value for each Champion a player has played"""
        data = self._create_request('getchampionranks', [player_id])
        return data

    def get_player_loadouts(self, player_id: List[str]) -> list:
        """Returns deck loadouts per Champion"""
        data = self._create_request('getplayerloadouts', [player_id, self.lang_code])
        return data

    def get_player_id(self, player_name: List[str]) -> list:
        """Returns a player id, which is used for other function calls"""
        data = self._create_request('getplayeridbyname', [player_name])
        try:
            return [data[0]['player_id']]
        except KeyError and IndexError:
            print('Player not found')


class SmiteAPI(HiRezAPI):
    base_url = 'http://api.smitegame.com/smiteapi.svc/'

    def __init__(self, dev_id: str, auth_key: str):
        """Session is not created until a request is made"""
        self.dev_id = dev_id
        self.auth_key = auth_key
        self.base_url = SmiteAPI.base_url
        self.session_id = None
        self.lang_code = '1'

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

    def get_god_ranks(self, player_id: List[str]) -> list:
        """Returns the Rank and Worshippers value for each God a player has played"""
        data = self._create_request('getgodranks', [player_id])
        return data

    def get_player_achievements(self, player_id: List[str]) -> dict:
        """Returns select achievement totals for the specified playerId"""
        data = self._create_request('getplayerachievements', [player_id])
        return data

    def search_teams(self, clan_name: List[str]) -> list:
        """Returns high level information for Clan names containing the Clan name"""
        data = self._create_request('searchteams', [clan_name])
        return data

    def get_motd(self) -> list:
        """Returns information about the 20 most recent Match-of-the-Days"""
        data = self._create_request('getmotd')
        return data
