import json
import webapp2
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
import routes.user
import routes.clan


def player_exists(player_tag):
    for player in Player.query(Player.tag == player_tag):
        return True
    return False


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



def authenticate_user(header_obj):
    print header_obj
    if 'auth' in header_obj:
        for user in routes.user.User.query(routes.user.User.api_key == header_obj['auth']):
            return True
    return False

def get_clan_from_tag(tag):
    for clan in routes.clan.Clan.query(routes.clan.Clan.clan_tag == tag):
        return clan.id
    return ''

PLAYER_LINK = "https://api.royaleapi.com/player/"
ROYALE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTQyMywiaWRlbiI6IjM5Njg5NDk4OTY5Njc2MTg3MSIsIm1kIjp7InVzZXJuYW1lIjoidWJlciIsImtleVZlcnNpb24iOjMsImRpc2NyaW1pbmF0b3IiOiIyOTI5In0sInRzIjoxNTM4Mjc0MjQxOTUyfQ.Omtc0zqvPJdrTnPyLgg7Dk_jwq0Rf1UDkrJ6y8QZzAE"



class Player(ndb.Model):
    id = ndb.StringProperty()
    tag = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    trophies = ndb.IntegerProperty(required=True)
    donations = ndb.IntegerProperty(required=True)
    donations_delta = ndb.IntegerProperty(required=True)
    clan = ndb.StringProperty()
    

class PlayerHandler(webapp2.RequestHandler):
    def options(self, player_id=None):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'auth, Authorization'
        self.response.headers['Access-Control-Allow-Methods'] = '*'
        
    def get(self, player_id=None):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'auth, Authorization'
        self.response.headers['Access-Control-Allow-Methods'] = '*'
        if not player_id:
            # show all players
            player_list = [all_players.to_dict()
                           for all_players in Player.query()]
            for player in player_list:
                player['self'] = "/players/" + str(player['id'])
            self.response.write(json.dumps(player_list))
        if len(player_id) < 12:
            selected_player = royale_api_get(
                PLAYER_LINK + player_id)
            if not selected_player:
                self.response.status = 400
                self.response.write("ERROR: CANNOT ACCESS API")
            self.response.write(selected_player)
        else:
            if not authenticate_user(self.request.headers):
                self.response.status = 403
                self.response.write("ERROR: Cannot authenticate")
            api_key = self.request.headers['auth']
            selected_player = ndb.Key(urlsafe=player_id).get()
            if not selected_player:
                self.response.status = 404
                self.response.write("ERROR: player does not exist")
            player_dict = selected_player.to_dict()
            player_dict['self'] = "/players/" + selected_player.id
            self.response.write(json.dumps(player_dict))


    def post(self):
        if not authenticate_user(self.request.headers):
            self.response.status = 403
            self.response.write("ERROR: cannot be authenticated")
        body = json.loads(self.request.body)
        if 'tag' not in body:
            self.response.status = 400
            self.response.write("ERROR: no player tag provided")
        if player_exists(body['tag']):
            self.response.status = 400
            self.response.write("ERROR: player already exists")
        #auto populate add player info
        player_json = royale_api_get(PLAYER_LINK + body['tag'])
        player_data = json.loads(player_json)
        new_player = Player(
            tag=player_data['tag'],
            name=player_data['name'],
            trophies=player_data['trophies'],
            donations=player_data['clan']['donations'],
            donations_delta=player_data['clan']['donationsDelta'],
            clan=player_data['clan']['tag'].upper()
        )
        new_player.put()
        new_player.id = str(new_player.key.urlsafe())
        new_player.put()
        new_player_dict = new_player.to_dict()
        new_player_dict['self'] = "/players/" + new_player.id
        self.response.write(json.dumps(new_player_dict))



    def put(self, player_id=None):
        if authenticate_user(self.request.headers):
            body = json.loads(self.request.body)
        else:
            self.response.status = 400
            self.response.write("ERROR: cannot be authenticated")
        if 'tag' not in body:
            self.response.status = 400
            self.response.write("ERROR: missing tag in body")
        if player_exists(body['tag']):
            self.response.status = 400
            self.response.write("ERROR: player exists already")
        #get player
        if not player_id:
            self.response.status = 400
            self.response.write("ERROR: no player_id given")
        selected_player = ndb.Key(urlsafe=player_id).get()
        if not selected_player:
            self.response.status = 400
            self.response.write("ERROR: player_id does not exist")
        player_json = royale_api_get(PLAYER_LINK + body['tag'])
        player_data = json.loads(player_json)
        selected_player.tag = player_data['tag']
        selected_player.name = player_data['name']
        selected_player.trophies = player_data['trophies']
        selected_player.donations = player_data['clan']['donations']
        selected_player.donations_delta = player_data['clan']['donationsDelta']
        selected_player.clan = player_data['clan']['tag'].upper()
        selected_player.put()
        player_dict = selected_player.to_dict()
        self.response.write(json.dumps(player_dict))

    def delete(self, player_id=None):
        #needs to handle removing player from clan entity
        if not authenticate_user(self.request.headers):
            self.response.status = 403
            self.response.write("ERROR: cannot authenticate")
        if not player_id:
            self.response.status = 400
            self.response.write("ERROR: missing player_id")
        selected_player = ndb.Key(urlsafe=player_id).get()
        if not selected_player:
            self.response.status = 400
            self.response.write("ERROR: player_id does not exist")
        if selected_player.clan:
            clan_id = get_clan_from_tag(selected_player.clan)
            if clan_id:
                selected_clan = ndb.Key(urlsafe=clan_id).get()
                #remove member from clan
                for idx, member in enumerate(selected_clan.members):
                    if member.id == player_id:
                        delete_index = idx
                del selected_clan.members[delete_index]
                selected_clan.put()
        selected_player.key.delete()
        self.response.write("Deleted player: " + str(player_id))
        



