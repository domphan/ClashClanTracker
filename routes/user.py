import json
from google.appengine.ext import ndb
import webapp2
import os
from models.user import User
from helpers.user_helpers import *

PLAYER_LINK = "https://api.royaleapi.com/player/"

class UserHandler(webapp2.RequestHandler):
    def options(self, tag=None):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = "*"
        self.response.headers['Access-Control-Allow-Methods'] = '*'

    # get should return all of player's favorite
    def get(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = "*"
        self.response.headers['Access-Control-Allow-Methods'] = '*'
        # check for auth header
        if 'auth' not in self.request.headers:
            self.response.status = 403
            self.response.write("ERROR: MISSING API KEY IN REQUEST HEADER")
            return
        # authenticate user
        user = authenticate_user(self.request.headers)
        if not user:
            self.response.status = 403
            self.response.write("ERROR: INVALID AUTHENTICATION")
            return
        if not user:
            self.response.status = 404
            self.response.write("ERROR: User does not exist")
            return
        user_dict = user.to_dict()
        if user_dict.get('favorites'):
            favorites = {}
            for item in user_dict['favorites']:
                favorites[item] = json.loads(rate_limited_fetch(PLAYER_LINK + item))
                delete_from_obj = ['deckLink', 'cards', 'achievements']
                for key in delete_from_obj:
                    try:
                        favorites[item].pop(key)
                    except KeyError:
                        pass
            self.response.write(json.dumps(favorites))
            return
        else:
            self.response.write([])

        
    # post to add players to the user's favorites
    def post(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = "*"
        self.response.headers['Access-Control-Allow-Methods'] = '*'
        # check for auth header
        if 'auth' not in self.request.headers:
            self.response.status = 403
            self.response.write("ERROR: MISSING API KEY IN REQUEST HEADER")
            return
        # authenticate user
        user = authenticate_user(self.request.headers)
        if not user:
            self.response.status = 403
            self.response.write("ERROR: INVALID AUTHENTICATION")
            return
        if not user:
            self.response.status = 404
            self.response.write("ERROR: User does not exist")
            return
        # check for player tag in body
        body = json.loads(self.request.body)
        if 'player_tag' not in body:
            self.response.status = 400
            self.response.write("ERROR: NO PLAYER TAG IN BODY TO ADD")
            return
        # add player to list
        user.favorites.append(body['player_tag'])
        user.put()
        # create a player object to DB
        """
        FIX THIS
        """
        #routes.player.add_player(body['player_tag'])
        # send json response
        user_dict = user.to_dict()
        self.response.write(json.dumps(user_dict['favorites']))

    # delete to remove players or a single player from user's favorites
    def delete(self, player_tag=None):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = "*"
        self.response.headers['Access-Control-Allow-Methods'] = '*'
        # check for auth header
        if 'auth' not in self.request.headers:
            self.response.status = 403
            self.response.write("ERROR: MISSING API KEY IN REQUEST HEADER")
            return
        # authenticate user
        user = authenticate_user(self.request.headers)
        if not user:
            self.response.status = 403
            self.response.write("ERROR: INVALID AUTHENTICATION")
            return
        if not user:
            self.response.status = 404
            self.response.write("ERROR: User does not exist")
            return
        # delete all
        if player_tag is None:
            user['favorites'] = []
            user.put()
            self.response.write("User's favorite players deleted")
            return
        # delete single
        if player_tag:
            for idx, player in enumerate(user.favorites):
                if player_tag == player:
                    delete_index = idx
                    break
            del user.favorites[delete_index]
            user.put()
            self.response.write(("Player {} has been removed from favorites").format(player_tag))
