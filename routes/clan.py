import json
import webapp2
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from routes.player import Player
from routes.user import User

ROYALE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTQyMywiaWRlbiI6IjM5Njg5NDk4OTY5Njc2MTg3MSIsIm1kIjp7fSwidHMiOjE1MzM2NjAzNzY2NDN9.5Vur0CS8gOqiU7-OgL3KZocWFKsLFgOtPUt_Du-bIDE"

def authenticate_user(header_obj):
    print header_obj
    if 'auth' in header_obj:
        for user in User.query(User.api_key == header_obj['auth']):
            return True
    return False

def get_authenticated_clan(api_key):
    for user in User.query(User.api_key == api_key):
        return user.clan_id
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

class Clan(ndb.Model):
    id = ndb.StringProperty()
    owner_id = ndb.StringProperty()
    name = ndb.StringProperty(required=True)
    clan_tag = ndb.StringProperty(required=True)
    member_amount = ndb.IntegerProperty(required=True)
    members = ndb.StructuredProperty(Player, repeated=True)
    donations_per_week = ndb.IntegerProperty(required=True)
    
class ClanHandler(webapp2.RequestHandler):
    
    def get(self, tag=None):
        # get clan from royale_api
        if tag:
            selected_clan = royale_api_get("https://api.royaleapi.com/clan/" + tag)
            self.response.write(selected_clan)
        # check for auth
        else:
            if authenticate_user(self.request.headers):
                api_key = self.request.headers['auth']
                # get clan id
                owner_clan_id = get_authenticated_clan(api_key)
                if owner_clan_id:
                    # if it exists, get db object
                    selected_clan = ndb.Key(urlsafe=owner_clan_id).get()
                    if selected_clan:
                        # return to user
                        clan_dict = selected_clan.to_dict()
                        clan_dict['self'] = "/clans/" + owner_clan_id
                        self.response.write(json.dumps(clan_dict))
                    else:
                        # does not exist
                        self.response.status = 404
                        self.response.write(
                            "ERORR: " + selected_clan + " does not exist")    
                else:
                # return empty object if clan not created yet
                    clan_dict = {}
                    self.response.write(json.dumps(clan_dict))
            else:
                self.response.status = 404
                self.response.write("ERROR 404: Auth error")


    def post(self):
        if authenticate_user(self.request.headers):
            api_key = self.request.headers['auth']
            # allow user to post a clan, need to populate everything else
            body = json.loads(self.request.body)
            if 'tag' in body and not clan_owned_already(body['tag']):
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
                        donations_delta = member['donationsDelta'],
                        clan=clan_data['tag'].upper()
                    )
                    new_clan.members.append(new_member)
                    new_member.put()
                    new_member.id = str(new_member.key.urlsafe())
                    new_member.put()
                # add to list for clan
                new_clan.put()
                # response JSON
                new_clan_dict = new_clan.to_dict()
                new_clan_dict['self'] = "/clans/" + new_clan.key.urlsafe()
                self.response.write(json.dumps(new_clan_dict))
            else:
                self.response.status = 400
                self.response.write(
                    "ERROR 400: MISSING CLAN TAG OR CLAN CREATED ALREADY")
        else:
            self.response.status = 403
            self.response.write("ERROR: CANNOT BE AUTHENTICATED")


    def put(self, clan_id=None):
        if authenticate_user(self.request.headers):
            api_key = self.request.headers['auth']
            body = json.loads(self.request.body)
            if 'tag' in body and not clan_owned_already(body['tag']):
                if clan_id:
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
                            new_member.put()
                            new_member.id = str(new_member.key.urlsafe())
                            new_member.put()
                        selected_clan.put()
                        clan_dict = selected_clan.to_dict()
                        clan_dict['self'] = "/clans/" + selected_clan.key.urlsafe()
                        self.response.write(json.dumps(clan_dict))
                    else:
                        self.response.status = 400
                        self.response.write("ERROR CLAN DOESN'T EXIST")
                else:
                    self.response.status = 400
                    self.response.write("ERROR NO CLAN_ID IN URL")
            else:
                self.response.status = 400
                self.response.write("ERROR: NO CLAN TAG IN BODY OR CLAN ALREADY OWNED")
        else:
            self.response.status = 400
            self.response.write("ERROR: CANNOT AUTHENTICATE")

    # needs to handle removing clans from players
    def delete(self, clan_id=None):
