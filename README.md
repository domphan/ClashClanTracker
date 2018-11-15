# ClashClanTracker - 
#### A web API used for gathering and storing clan and player data from Clash Royale
<hr>

## Routes
URL = https://clashclantracker.appspot.com

__Users__
GET             URL/users
* Returns a json of the user's favorited players.
* params: none

POST            URL/users
* Adds a player to the user's list of favorited players.
* params: ```{player_tag: "tag"}```

DEL             URL/users/:tag
* Removes a specific player based on tag from user's favorites
* params: ```{player_tag: "tag"}```

DEL             URL/users
* Remove all players from user's favorites
* params: none


__Clans__
__Players__
