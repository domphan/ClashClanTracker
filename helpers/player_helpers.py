import json
import webapp2
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from models.user import User
from models.player import Player
from models.clan import Clan


# Queries database to check if user exists
def authenticate_user(header_obj):
    if 'auth' in header_obj:
        for _ in User.query(User.api_key == header_obj['auth']):
            return True
    return False


def get_clan_from_tag(tag):
    for clan in Clan.query(Clan.clan_tag == tag):
        return clan.id
    return ''

def player_exists(player_tag):
    for _ in Player.query(Player.tag == player_tag):
        return True
    return False


def get_user(api_key):
    for user in User.query(User.api_key == api_key):
        return user.id
    return False

# used to fetch data from 3rd party API
def royale_api_get(url):
    try:
        access_header = {'auth': ROYALE}
        selected_item = urlfetch.fetch(
            url=url,
            headers=access_header
        )
        return selected_item.content
    except urlfetch.DeadlineExceededError:
        return ''


PLAYER_LINK = "https://api.royaleapi.com/player/"
with open("./secret/client_secrets.json") as data_file:
    data = json.load(data_file)

ROYALE = data["royale_api_key"]
