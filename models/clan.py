from google.appengine.ext import ndb
from models.player import Player

class Clan(ndb.Model):
    id = ndb.StringProperty()
    owner_id = ndb.StringProperty()
    name = ndb.StringProperty(required=True)
    clan_tag = ndb.StringProperty(required=True)
    member_amount = ndb.IntegerProperty(required=True)
    members = ndb.StructuredProperty(Player, repeated=True)
    donations_per_week = ndb.IntegerProperty(required=True)
    inactive_members = ndb.StringProperty()
    weakest_link = ndb.StringProperty()
