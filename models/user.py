from google.appengine.ext import ndb

class User(ndb.Model):
    id = ndb.StringProperty()
    email = ndb.StringProperty(required=True)
    clan_id = ndb.StringProperty()
    clan_tag = ndb.StringProperty()
    api_key = ndb.StringProperty(required=True)
    favorites = ndb.StringProperty(repeated=True)
