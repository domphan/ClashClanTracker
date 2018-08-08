import json
import webapp2
from google.appengine.ext import ndb

class Player(ndb.Model):
    id = ndb.StringProperty()
    tag = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    stats_clan_war = ndb.IntegerProperty(required=True)
    participation_clan_war = ndb.IntegerProperty(required=True)
    trophies = ndb.IntegerProperty(required=True)
    
