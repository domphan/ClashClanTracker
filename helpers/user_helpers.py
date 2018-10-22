import os
from binascii import hexlify
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from models.user import User


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
        api_key=generate_api_key(),
        favorites=[]
    )
    new_user.put()
    new_user.id = str(new_user.key.urlsafe())
    new_user.put()
    return new_user.api_key


def retrieve_api_key(email):
    for user in User.query(User.email == email):
        return user.api_key
    return ''
