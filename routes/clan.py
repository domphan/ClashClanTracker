import json
import webapp2
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from models.user import User
from models.clan import Clan
from models.player import Player
from helpers.clan_helpers import *

urlfetch.set_default_fetch_deadline(45)


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
            return
        # check for auth
        else:
            if not authenticate_user(self.request.headers):
                self.response.status = 403
                self.response.write("ERROR 403: Auth error")
                return
            api_key = self.request.headers['auth']
            # get clan id
            owner_clan_id = get_authenticated_clan(api_key)
            if not owner_clan_id:
                # return empty object if clan not created yet
                clan_dict = {}
                self.response.write(json.dumps(clan_dict))
                return
            # if it exists, get db object
            selected_clan = ndb.Key(urlsafe=owner_clan_id).get()
            if not selected_clan:
                # does not exist
                self.response.status = 404
                self.response.write("ERORR: clan does not exist")
                return
            # return to user
            clan_dict = selected_clan.to_dict()
            clan_dict['self'] = "/clans/" + owner_clan_id
            self.response.write(json.dumps(clan_dict))



    def post(self):
        if not authenticate_user(self.request.headers):
            self.response.status = 403
            self.response.write("ERROR: CANNOT BE AUTHENTICATED")
            return
        api_key = self.request.headers['auth']
        # allow user to post a clan, need to populate everything else
        body = json.loads(self.request.body)
        if 'tag' not in body: 
            self.response.status = 400
            self.response.write("ERROR 400: MISSING CLAN TAG")
            return
        if clan_owned_already(body['tag']):
            self.response.status = 400
            self.response.write("ERROR: CLAN OWNED ALREADY")
            return
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
        for user in User.query(User.api_key == api_key):
            user.clan_id = new_clan.id
            user.clan_tag = clan_data['tag'].upper()
            user.put()
        # for each member
        for member in clan_data['members']:
            # create new entity
            new_member = Player(
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
        # authenticate user
        if not authenticate_user(self.request.headers):
            self.response.status = 403
            self.response.write("ERROR: cannot authenticate")
            return
        api_key = self.request.headers['auth']
        body = json.loads(self.request.body)
        # check if user sent in tag 
        if 'tag' not in body:
            self.response.status = 400
            self.response.write("ERROR: NO CLAN TAG IN BODY")
            return
        # check if clan is owned already
        if clan_owned_already(body['tag']):
            owner_tag = get_authenticated_clan_tag(api_key)
            # if it exists, check if the owner is being sent in
            if owner_tag != body['tag']:
                self.response.status = 400
                self.response.write("ERROR: CLAN ALREADY OWNED")
                return
        # check if clan id in URI
        if not clan_id:
            self.response.status = 400
            self.response.write("ERROR NO CLAN_ID IN URL")
            return
        # look in db for key
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
                new_member = Player(
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
            return
        else:
            self.response.status = 400
            self.response.write("ERROR CLAN DOESN'T EXIST")
            return

    # needs to handle removing clans from players
    def delete(self, clan_id=None):
        if not authenticate_user(self.request.headers):
            self.response.status = 401
            self.response.write("ERROR: CANNOT AUTHENTICATE")
            return
        api_key = self.request.headers['auth']
        if not clan_id:
            self.response.status = 400
            self.response.write("Error: missing clan id")
            return
        selected_clan = ndb.Key(urlsafe=clan_id).get()
        if not selected_clan:
            self.response.status = 400
            self.response.write("Error: invalid clan id")
            return
        # remove clan from user
        clear_clan_user(api_key)
        selected_clan.key.delete()
        self.response.write(
            "Deleted clan :" +
            str(clan_id) + " cleared players' clan"
            + " and removed clan from user account"
        )
