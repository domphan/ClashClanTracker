from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
import routes.user
from routes.clan import ClanHandler
from routes.player import PlayerHandler
from routes.user import UserHandler
import webapp2
import json
import urllib
import random
import string
import os

with open("secret/client_secrets.json") as data_file:
    data = json.load(data_file)
CLIENT_ID = data["web"]["client_id"]
CLIENT_SECRET = data["web"]["client_secret"]
# REDIRECT_URI = "http://localhost:8080/oauth"
OAUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
STATE_STRING = ""
REDIRECT_URI = "https://clashclantracker.appspot.com/oauth"
# [START main_page]


def get_random_state():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))


class HomePageHandler(webapp2.RequestHandler):
    def get(self):
        STATE_STRING = get_random_state()
        app.registry["state"] = STATE_STRING
        url = OAUTH_URL + "?" + "response_type=code&" + \
            "client_id=" + CLIENT_ID + "&" + \
            "redirect_uri=" + REDIRECT_URI + "&" + \
            "scope=email&" + "state=" + STATE_STRING
        template_values = {'url': url}
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values))


class OAuthHandler(webapp2.RequestHandler):
    def get(self):
        state = self.request.get('state')
        code = self.request.get('code')
        if state != app.registry["state"]:
            self.response.write("ERROR 403: FORBIDDEN")
            self.response.set_status(403)
            return
        post_header = {'Content-type': 'application/x-www-form-urlencoded'}
        post_body = {
            'code': code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        payload = urllib.urlencode(post_body)
        post_result = urlfetch.fetch(
            method=urlfetch.POST,
            url="https://www.googleapis.com/oauth2/v4/token/",
            headers=post_header,
            payload=payload
        )
        oauth_access_token = json.loads(post_result.content)
        access_header = {'Authorization': 'Bearer ' +
                                          oauth_access_token['access_token']}
        user_result = urlfetch.fetch(
            url="https://www.googleapis.com/plus/v1/people/me",
            headers=access_header
        )
        accessed_properties = json.loads(user_result.content)
        accessed_properties['image']['url'] = accessed_properties['image']['url'].replace(
            "sz=50", "sz=240")
        #print accessed_properties
        email = accessed_properties['emails'][0]['value']
        # check if user has account / api key already
        api_key = routes.user.retrieve_api_key(email)
        if not api_key:
            # generate API_KEY for user
            api_key = routes.user.create_user(email)
        # append api key so template can receive
        accessed_properties.update({'api_key': api_key})
        template_values = {'object': accessed_properties}
        path = os.path.join(os.path.dirname(__file__),
                            'templates/grant_api_key.html')
        self.response.out.write(template.render(path, template_values))

# [START patch]
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
# [END patch]

# [START app]
app = webapp2.WSGIApplication([
    ('/', HomePageHandler),
    ('/oauth', OAuthHandler),
    ('/clans', ClanHandler),
    ('/clans/(.*)', ClanHandler),
    ('/players', PlayerHandler),
    ('/players/(.*)', PlayerHandler),
    ('/favorites', UserHandler),
    ('/favorites/(.*)', UserHandler)
], debug=True)
# [END app]
