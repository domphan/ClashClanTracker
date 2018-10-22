from google.appengine.ext import ndb

class Player(ndb.Model):
    id = ndb.StringProperty()
    tag = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    trophies = ndb.IntegerProperty(required=True)
    donations = ndb.IntegerProperty(required=True)
    donations_delta = ndb.IntegerProperty(required=True)
    clan = ndb.StringProperty()
