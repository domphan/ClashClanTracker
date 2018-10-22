from google.appengine.ext import ndb

class Player(ndb.Model):
    id = ndb.StringProperty()
    tag = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    trophies = ndb.IntegerProperty(required=True)
    donations = ndb.IntegerProperty()
    donations_delta = ndb.IntegerProperty()
    clan = ndb.StringProperty()
