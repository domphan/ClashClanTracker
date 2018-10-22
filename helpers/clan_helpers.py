import json
import webapp2
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from models.user import User
from models.player import Player
from models.clan import Clan

urlfetch.set_default_fetch_deadline(45)

with open("./secret/client_secrets.json") as data_file:
    data = json.load(data_file)

ROYALE = data["royale_api_key"]
REALLY_LARGE_NUMBER = 500000


def authenticate_user(header_obj):
    if 'auth' in header_obj:
        for user in User.query(User.api_key == header_obj['auth']):
            return True
    return False


def get_authenticated_clan(api_key):
    for user in User.query(User.api_key == api_key):
        return user.clan_id
    return ''


def get_authenticated_clan_tag(api_key):
    for user in User.query(User.api_key == api_key):
        return user.clan_tag
    return ''


def royale_api_get(url):
    access_header = {'auth': ROYALE}
    selected_item = urlfetch.fetch(
        url=url,
        headers=access_header
    )
    return selected_item.content


def clan_owned_already(clan_tag):
    for user in User.query(User.clan_tag == clan_tag):
        return True
    return False


def get_owner_id(api_key):
    for user in User.query(User.api_key == api_key):
        return user.id
    return ""


def clear_clan_user(api_key):
    for user in User.query(User.api_key == api_key):
        user.clan_id = None
        user.clan_tag = None
        user.put()


def get_weakest_link(members):
    minimum_delta = REALLY_LARGE_NUMBER
    minimum_player = None
    for member in members:
        if member.donations_delta < minimum_delta:
            minimum_delta = member.donations_delta
            minimum_player = member
    return minimum_player.name


def get_inactive_players(members):
    inactive_string = ""
    for member in members:
        if member.donations == 0:
            inactive_string = inactive_string + \
                member.name.encode('utf-8') + ", "
    return inactive_string[:-2]
