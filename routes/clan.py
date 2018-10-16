import json
import webapp2
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
import routes.player
import routes.user

urlfetch.set_default_fetch_deadline(45)

ROYALE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTQyMywiaWRlbiI6IjM5Njg5NDk4OTY5Njc2MTg3MSIsIm1kIjp7InVzZXJuYW1lIjoidWJlciIsImtleVZlcnNpb24iOjMsImRpc2NyaW1pbmF0b3IiOiIyOTI5In0sInRzIjoxNTM4Mjc0MjQxOTUyfQ.Omtc0zqvPJdrTnPyLgg7Dk_jwq0Rf1UDkrJ6y8QZzAE"
REALLY_LARGE_NUMBER = 500000


def authenticate_user(header_obj):
    if 'auth' in header_obj:
        for user in routes.user.User.query(routes.user.User.api_key == header_obj['auth']):
            return True
    return False


def get_authenticated_clan(api_key):
    for user in routes.user.User.query(routes.user.User.api_key == api_key):
        return user.clan_id
    return ''


def get_authenticated_clan_tag(api_key):
    for user in routes.user.User.query(routes.user.User.api_key == api_key):
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
    for user in routes.user.User.query(routes.user.User.clan_tag == clan_tag):
        return True
    return False


def get_owner_id(api_key):
    for user in routes.user.User.query(routes.user.User.api_key == api_key):
        return user.id
    return ""

def clear_clan_user(api_key):
    for user in routes.user.User.query(routes.user.User.api_key == api_key):
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


class Clan(ndb.Model):
    id = ndb.StringProperty()
    owner_id = ndb.StringProperty()
    name = ndb.StringProperty(required=True)
    clan_tag = ndb.StringProperty(required=True)
    member_amount = ndb.IntegerProperty(required=True)
    members = ndb.StructuredProperty(routes.player.Player, repeated=True)
    donations_per_week = ndb.IntegerProperty(required=True)
    inactive_members = ndb.StringProperty()
    weakest_link = ndb.StringProperty()


class ClanHandler(webapp2.RequestHandler):
    def options(self, clan_id=None):
        self.response.headers['Access-Control-Allow-Origin'] = "*"
        self.response.headers['Access-Control-Allow-Headers'] = '*'
        self.response.headers['Access-Control-Allow-Methods'] = '*'
        
    def get(self, tag=None):
        self.response.headers['Access-Control-Allow-Origin'] = "*"
        self.response.headers['Access-Control-Allow-Headers'] = '*'
        self.response.headers['Access-Control-Allow-Methods'] = '*'
        # get clan from royale_api
        if tag:
            selected_clan = royale_api_get(
                "https://api.royaleapi.com/clan/" + tag)
            self.response.write(selected_clan)
        # check for auth
        else:
            if not authenticate_user(self.request.headers):
                self.response.status = 403
                self.response.write("ERROR 403: Auth error")
            api_key = self.request.headers['auth']
            # get clan id
            owner_clan_id = get_authenticated_clan(api_key)
            if not owner_clan_id:
                # return empty object if clan not created yet
                clan_dict = {}
                self.response.write(json.dumps(clan_dict))
            # if it exists, get db object
            selected_clan = ndb.Key(urlsafe=owner_clan_id).get()
            if not selected_clan:
                # does not exist
                self.response.status = 404
                self.response.write("ERORR: clan does not exist")
            # return to user
            clan_dict = selected_clan.to_dict()
            clan_dict['self'] = "/clans/" + owner_clan_id
            self.response.write(json.dumps(clan_dict))



    def post(self):
        if not authenticate_user(self.request.headers):
            self.response.status = 403
            self.response.write("ERROR: CANNOT BE AUTHENTICATED")
        api_key = self.request.headers['auth']
        # allow user to post a clan, need to populate everything else
        body = json.loads(self.request.body)
        if 'tag' not in body: 
            self.response.status = 400
            self.response.write(
                "ERROR 400: MISSING CLAN TAG")
        if clan_owned_already(body['tag']):
            self.response.status = 400
            self.response.write("ERROR: CLAN OWNED ALREADY")
        # populate clan data
        clan_json = royale_api_get(
            "https://api.royaleapi.com/clan/" + body['tag'])
        clan_data = json.loads(clan_json)
        # create new clan
        new_clan = Clan(
            owner_id=get_owner_id(api_key),
            name=clan_data['name'],
            clan_tag=clan_data['tag'].upper(),
            member_amount=clan_data['memberCount'],
            donations_per_week=clan_data['donations'],
            members=[]
        )
        new_clan.put()
        new_clan.id = str(new_clan.key.urlsafe())
        new_clan.put()
        # add clan to user
        for user in routes.user.User.query(routes.user.User.api_key == api_key):
            user.clan_id = new_clan.id
            user.clan_tag = clan_data['tag'].upper()
            user.put()
        # for each member
        for member in clan_data['members']:
            # create new entity
            new_member = routes.player.Player(
                tag=member['tag'],
                name=member['name'],
                trophies=member['trophies'],
                donations=member['donations'],
                donations_delta=member['donationsDelta'],
                clan=clan_data['tag'].upper()
            )
            new_clan.members.append(new_member)
            new_clan.weakest_link = get_weakest_link(new_clan.members)
            new_clan.inactive_members = get_inactive_players(
                new_clan.members)
        # add to list for clan
        new_clan.put()
        # response JSON
        new_clan_dict = new_clan.to_dict()
        new_clan_dict['self'] = "/clans/" + new_clan.id
        self.response.write(json.dumps(new_clan_dict))


    def put(self, clan_id=None):
        self.response.headers['Access-Control-Allow-Origin'] = "*"
        self.response.headers['Access-Control-Allow-Headers'] = '*'
        self.response.headers['Access-Control-Allow-Methods'] = '*'
        if not authenticate_user(self.request.headers):
            self.response.status = 403
            self.response.write("ERROR: cannot authenticate")
        api_key = self.request.headers['auth']
        body = json.loads(self.request.body)
        if 'tag' not in body:
            self.response.status = 400
            self.response.write(
                "ERROR: NO CLAN TAG IN BODY")
        if clan_owned_already(body['tag']):
            owner_tag = get_authenticated_clan_tag(api_key)
            if owner_tag != body['tag']:
                self.response.status = 400
                self.response.write("ERROR: CLAN ALREADY OWNED")
        if not clan_id:
            self.response.status = 400
            self.response.write("ERROR NO CLAN_ID IN URL")
        selected_clan = ndb.Key(urlsafe=clan_id).get()
        if selected_clan:
            clan_json = royale_api_get(
                "https://api.royaleapi.com/clan/" + body['tag'])
            clan_data = json.loads(clan_json)
            selected_clan.owner_id = get_owner_id(api_key)
            selected_clan.name = clan_data['name']
            selected_clan.clan_tag = clan_data['tag'].upper()
            selected_clan.member_amount = clan_data['memberCount']
            selected_clan.donations_per_week = clan_data['donations']
            selected_clan.members = []
            for member in clan_data['members']:
                new_member = routes.player.Player(
                    tag=member['tag'],
                    name=member['name'],
                    trophies=member['trophies'],
                    donations=member['donations'],
                    donations_delta=member['donationsDelta'],
                    clan=clan_data['tag'].upper()
                )
                selected_clan.members.append(new_member)
            selected_clan.inactive_members = get_inactive_players(selected_clan.members)
            selected_clan.weakest_link = get_weakest_link(selected_clan.members)
            selected_clan.put()
            clan_dict = selected_clan.to_dict()
            clan_dict['self'] = "/clans/" + selected_clan.key.urlsafe()
            self.response.write(json.dumps(clan_dict))
        else:
            self.response.status = 400
            self.response.write("ERROR CLAN DOESN'T EXIST")

    # needs to handle removing clans from players
    def delete(self, clan_id=None):
        if not authenticate_user(self.request.headers):
            self.response.status = 401
            self.response.write("ERROR: CANNOT AUTHENTICATE")
        api_key = self.request.headers['auth']
        if not clan_id:
            self.response.status = 400
            self.response.write("Error: missing clan id")    
        selected_clan = ndb.Key(urlsafe=clan_id).get()
        if not selected_clan:
            self.response.status = 400
            self.response.write("Error: invalid clan id")
        # remove clan from user
        clear_clan_user(api_key)
        selected_clan.key.delete()
        self.response.write(
            "Deleted clan :" +
            str(clan_id) + " cleared players' clan"
            + " and removed clan from user account"
        )
