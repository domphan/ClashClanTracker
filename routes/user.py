from google.appengine.ext import ndb
import json
import webapp2

class User(ndb.Model):
    id = ndn.StringProperty()
    email = ndb.StringProperty(required=True)
    clan = ndb.StringProperty()
