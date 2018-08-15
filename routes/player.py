import json
import webapp2
from google.appengine.ext import ndb
from routes.clan import Clan, authenticate_user, royale_api_get

PLAYER_LINK = "https://api.royaleapi.com/player/"

def player_exists(player_tag):
    for player in Player.query(Player.tag == player_tag):
        return True
    return False

class Player(ndb.Model):
    id = ndb.StringProperty()
    tag = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    trophies = ndb.IntegerProperty(required=True)
    donations = ndb.IntegerProperty(required=True)
    donations_delta = ndb.IntegerProperty(required=True)
    clan = ndb.StringProperty()
    

class PlayerHandler(webapp2.RequestHandler):

    def get(self, player_id=None):
        if player_id:
            if len(player_id) < 12:
                selected_player = royale_api_get(
                    PLAYER_LINK + player_id)
                self.response.write(selected_player)
            else:
                if authenticate_user(self.request.headers):
                    api_key = self.request.headers['auth']
                    selected_player = ndb.Key(urlsafe=player_id).get()
                    if selected_player:
                        player_dict = selected_player.to_dict()
                        player_dict['self'] = "/players/" + selected_player.id
                        self.response.write(json.dumps(player_dict))
                    else:
                        self.response.status = 404
                        self.response.write("ERROR: player does not exist")
                else:
                    self.response.status = 403
                    self.response.write("ERROR: Cannot authenticate")
        # show all players
        else:
            player_list = [all_players.to_dict() for all_players in Player.query()]
            for player in player_list:
                player['self'] = "/players/" + str(player['id'])
            self.response.write(json.dumps(player_list))

    def post(self):
        if authenticate_user(self.request.headers):
            api_key = self.request.headers['auth']
            body = json.loads(self.request.body)
            if 'tag' in body and not player_exists(body['tag']):
                if 'auto' in body:
                    #auto add player
                    player_json = royale_api_get(PLAYER_LINK + body['tag'])
                    player_data = json.loads(player_json)
                    new_player = Player(
                        tag=player_data['']
                    )
                else:
                    #manual add from paramters
