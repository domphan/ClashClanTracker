from google.appengine.ext import ndb
import json
import webapp2
import os
from models.user import User
from helpers.user_helpers import *

class UserHandler(webapp2.RequestHandler):
    def options(self):
        self.response.headers['Access-Control-Allow-Origin'] = "*"
        self.response.headers['Access-Control-Allow-Headers'] = '*'
        self.response.headers['Access-Control-Allow-Methods'] = '*'

    # get should return all of player's favorite
    def get(self):
        # check for auth header
        if 'auth' not in self.request.headers:
            self.response.status = 403
            self.repsonse.write("ERROR: MISSING API KEY IN REQUEST HEADER")
        # authenticate user
        user = authenticate_user(self.request.headers)
        user_dict = user.to_dict()
        if not user:
            self.response.status = 403
            self.response.write("ERROR: INVALID AUTHENTICATION")
        if not user:
            self.response.status = 404
            self.response.write("ERROR: User does not exist")
        if len(user_dict['favorites']) > 0:
            self.response.write(json.dumps(user_dict['favorites']))
        else:
            self.response.write([])

        
    # post to add players to the user's favorites
    def post(self):
        # check for auth header
        if 'auth' not in self.request.headers:
            self.response.status = 403
            self.repsonse.write("ERROR: MISSING API KEY IN REQUEST HEADER")
        # authenticate user
        user = authenticate_user(self.request.headers)
        if not user:
            self.response.status = 403
            self.response.write("ERROR: INVALID AUTHENTICATION")
        if not user:
            self.response.status = 404
            self.response.write("ERROR: User does not exist")
        # check for player tag in body
        body = json.loads(self.request.body)
        if 'player_tag' not in body:
            self.response.status = 400
            self.response.write("ERROR: NO PLAYER TAG IN BODY TO ADD")
        # add player to list
        user.favorites.append(body['player_tag'])
        user.put()
        # create a player object to DB
        #routes.player.add_player(body['player_tag'])
        # send json response
        user_dict = user.to_dict()
        self.response.write(json.dumps(user_dict['favorites']))

    # delete to remove players or a single player from user's favorites
    def delete(self, player_tag=None):
        # check for auth header
        if 'auth' not in self.request.headers:
            self.response.status = 403
            self.repsonse.write("ERROR: MISSING API KEY IN REQUEST HEADER")
        # authenticate user
        user = authenticate_user(self.request.headers)
        if not user:
            self.response.status = 403
            self.response.write("ERROR: INVALID AUTHENTICATION")
        if not user:
            self.response.status = 404
            self.response.write("ERROR: User does not exist")
        # delete all
        if player_tag is None:
            user['favorites'] = []
            user.put()
            self.response.write("User's favorite players deleted")
        # delete single
        if player_tag:
            for idx, player in enumerate(user.favorites):
                if player_tag == player:
                    delete_index = idx
                    break
            del user.favorites[delete_index]
            user.put()
            self.response.write(("Player {} has been removed from favorites").format(player_tag))
