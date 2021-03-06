import json
from ratelimit import limits
import webapp2
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from models.player import Player
from helpers.player_helpers import *


class PlayerHandler(webapp2.RequestHandler):
    def options(self, player_id=None):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'auth, Authorization'
        self.response.headers['Access-Control-Allow-Methods'] = '*'
    
    # Should return all favorited players of user, or just a single player from royaleAPI
    def get(self, player_id=None):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'auth, Authorization'
        self.response.headers['Access-Control-Allow-Methods'] = '*'
        if not player_id:
            # show all players
            player_list = [all_players.to_dict() for all_players in Player.query()]
            for player in player_list:
                player['self'] = "/players/" + str(player['id'])
            self.response.write(json.dumps(player_list))
            return
        # Get player data from 3rd party API
        if len(player_id) < 12:
            selected_player = royale_api_get(
                PLAYER_LINK + player_id)
            if not selected_player:
                self.response.status = 400
                self.response.write("ERROR: CANNOT ACCESS ROYALEAPI")
                return
            self.response.write(selected_player)
        # Get individual player from DB
        else:
            if not authenticate_user(self.request.headers):
                self.response.status = 403
                self.response.write("ERROR: Cannot authenticate")
                return
            api_key = self.request.headers['auth']
            selected_player = ndb.Key(urlsafe=player_id).get()
            if not selected_player:
                self.response.status = 404
                self.response.write("ERROR: player does not exist")
                return
            player_dict = selected_player.to_dict()
            player_dict['self'] = "/players/" + selected_player.id
            self.response.write(json.dumps(player_dict))

    # Add a favorite player to user as well
    def post(self):
        # Authentication check
        if not authenticate_user(self.request.headers):
            self.response.status = 403
            self.response.write("ERROR: cannot be authenticated")
            return
        # body parameter check
        body = json.loads(self.request.body)
        if 'tag' not in body:
            self.response.status = 400
            self.response.write("ERROR: no player tag provided")
            return
        if player_exists(body['tag']):
            self.response.status = 400
            self.response.write("ERROR: player already exists")
            return
        #auto populate add player info
        player_json = royale_api_get(PLAYER_LINK + body['tag'])
        player_data = json.loads(player_json)
        new_player = Player(
            tag=player_data['tag'],
            name=player_data['name'],
            trophies=player_data['trophies'],
            donations=player_data['clan']['donations'],
            donations_delta=player_data['clan']['donationsDelta'],
            clan=player_data['clan']['tag'].upper()
        )
        new_player.put()
        new_player.id = str(new_player.key.urlsafe())
        new_player.put()
        new_player_dict = new_player.to_dict()
        new_player_dict['self'] = "/players/" + new_player.id
        self.response.write(json.dumps(new_player_dict))


    # Used to refresh the player's individual stats
    def put(self, player_id=None):
        # authenticate
        if authenticate_user(self.request.headers):
            body = json.loads(self.request.body)
        else:
            self.response.status = 400
            self.response.write("ERROR: cannot be authenticated")
            return
        # check for player tag
        if 'tag' not in body:
            self.response.status = 400
            self.response.write("ERROR: missing tag in body")
            return
        # check given tag exists in DB already
        if player_exists(body['tag']):
            self.response.status = 400
            self.response.write("ERROR: player exists already")
            return
        # handle case with no player id
        if not player_id:
            self.response.status = 400
            self.response.write("ERROR: no player_id given")
            return
        selected_player = ndb.Key(urlsafe=player_id).get()
        # if player doesn't exist in DB
        if not selected_player:
            self.response.status = 400
            self.response.write("ERROR: player_id does not exist")
            return
        # load data and create dictionary from it
        player_json = royale_api_get(PLAYER_LINK + body['tag'])
        player_data = json.loads(player_json)
        selected_player.tag = player_data['tag']
        selected_player.name = player_data['name']
        selected_player.trophies = player_data['trophies']
        if player_data.get("clan"):
            selected_player.donations = player_data['clan']['donations']
            selected_player.donations_delta = player_data['clan']['donationsDelta']
            selected_player.clan = player_data['clan']['tag'].upper()
        else:
            selected_player.donations = None
            selected_player.donations_delta = None
            selected_player.clan = None
        selected_player.put()
        player_dict = selected_player.to_dict()
        self.response.write(json.dumps(player_dict))

    # remove selected player from DB
    def delete(self, player_id=None):
        #needs to handle removing player from clan entity
        if not authenticate_user(self.request.headers):
            self.response.status = 403
            self.response.write("ERROR: cannot authenticate")
            return
        # if no player_id in uri
        if not player_id:
            self.response.status = 400
            self.response.write("ERROR: missing player_id")
            return
        # get player frmo DB
        selected_player = ndb.Key(urlsafe=player_id).get()
        # if player doesn't exist in DB
        if not selected_player:
            self.response.status = 400
            self.response.write("ERROR: player_id does not exist")
            return
        # if player is in a clan, remove them
        if selected_player.clan:
            clan_id = get_clan_from_tag(selected_player.clan)
            if clan_id:
                selected_clan = ndb.Key(urlsafe=clan_id).get()
                #remove member from clan
                for idx, member in enumerate(selected_clan.members):
                    if member.id == player_id:
                        delete_index = idx
                del selected_clan.members[delete_index]
                selected_clan.put()
        # delete the player
        selected_player.key.delete()
        self.response.write("Deleted player: " + str(player_id))
        



