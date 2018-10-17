from google.appengine.ext import ndb
from binascii import hexlify
import json
import webapp2
import os


def authenticate_user(header_obj):
    if 'auth' in header_obj:
        for user in User.query(User.api_key == header_obj['auth']):
            return user
    return False

def generate_api_key():
    api_length = 16
    key = hexlify(os.urandom(api_length))
    return key.decode()
    
def create_user(email):
    new_user = User(
        email=email,
        api_key=generate_api_key()
    )
    new_user.put()
    new_user.id = str(new_user.key.urlsafe())
    new_user.put()
    return new_user.api_key
    
def retrieve_api_key(email):
    for user in User.query(User.email == email):
        return user.api_key
    return ''

class User(ndb.Model):
    id = ndb.StringProperty()
    email = ndb.StringProperty(required=True)
    clan_id = ndb.StringProperty()
    clan_tag = ndb.StringProperty()
    api_key = ndb.StringProperty(required=True)
    favorites = ndb.StringProperty(repeated=True)

class UserHandler(webapp2.RequestHandler):
    def options(self):
        self.response.headers['Access-Control-Allow-Origin'] = "*"
        self.response.headers['Access-Control-Allow-Headers'] = '*'
        self.response.headers['Access-Control-Allow-Methods'] = '*'

    # get should return all of player's favorite
    def get(self):
        # check for auth header
        if not self.request.headers.auth:
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
        self.response.wrte(json.dumps(user.favorites))

        
    # patch to add players to the user's favorites
    def patch(self):
        # check for auth header
        if not self.request.headers.auth:
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
        self.response.write(json.dumps(user.favorites))

    # delete to remove players or a single player from user's favorites
    def delete(self, player_tag=None):
        # check for auth header
        if not self.request.headers.auth:
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

