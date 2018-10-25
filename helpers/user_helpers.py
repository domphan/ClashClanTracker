import os
import json
from binascii import hexlify
from ratelimit import limits, sleep_and_retry
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from models.user import User

PLAYER_LINK = "https://api.royaleapi.com/player/"
with open("./secret/client_secrets.json") as data_file:
    data = json.load(data_file)
ROYALE = data["royale_api_key"] # my secret api key
ONE_SECOND = 1 # used for rate limit

# Authenticates the user with their api key
# Returns a user if successful
def authenticate_user(header_obj):
    if 'auth' in header_obj:
        for user in User.query(User.api_key == header_obj['auth']):
            return user
    return False

# Generates an API key for a newly registered user
def _generate_api_key():
    api_length = 16
    key = hexlify(os.urandom(api_length))
    return key.decode()

# Create user account and assigns an API key
def create_user(email):
    new_user = User(
        email=email,
        api_key=_generate_api_key(),
        favorites=[]
    )
    new_user.put()
    new_user.id = str(new_user.key.urlsafe())
    new_user.put()
    return new_user.api_key

# Retrieve API key with email
def retrieve_api_key(email):
    for user in User.query(User.email == email):
        return user.api_key
    return None

@sleep_and_retry
@limits(calls=5, period=ONE_SECOND)
def rate_limited_fetch(url):
    try:
        access_header = {'auth': ROYALE}
        response = urlfetch.fetch(
            url=url,
            headers=access_header
        )
        if response.status_code == 429:
            raise Exception('API response: {}'.format(response.status_code))
        return response.content
    except urlfetch.DeadlineExceededError:
        return 'deadline exceeded'
