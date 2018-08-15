from google.appengine.ext import ndb
from binascii import hexlify
import json
import webapp2
import os

def generate_api_key():
    api_length = 16
    key = hexlify(os.urandom(api_length))
    return key.decode()

class User(ndb.Model):
    id = ndb.StringProperty()
    email = ndb.StringProperty(required=True)
    clan_id = ndb.StringProperty()
    clan_tag = ndb.StringProperty()
    api_key = ndb.StringProperty(required=True)

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
    