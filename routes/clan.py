import json
import webapp2
from google.appengine.ext import ndb
from player import Player

class Clan(ndb.model):
    id = ndb.StringProperty()
    name = ndb.StringProperty(required=True)
    clan_tag = ndb.StringProperty(required=True)
    member_amount = ndb.IntegerProperty(required=True)
    members = ndb.StructuredProperty(Player, repeated=True)
    donations_per_week = ndb.IntegerProperty(required=True)
    


