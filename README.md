# ClashClanTracker - 
#### A web API used for gathering and storing clan and player data from Clash Royale
<hr>

## Routes
URL = https://clashclantracker.appspot.com

__Users__
<br>
**GET**             URL/users
* Returns a json of the user's favorited players.
* params: none

**POST**            URL/users
* Adds a player to the user's list of favorited players.
* params: ```{player_tag: "tag"}```

**DEL**             URL/users/:tag
* Removes a specific player based on tag from user's favorites
* params: ```{player_tag: "tag"}```

**DEL**             URL/users
* Remove all players from user's favorites
* params: none


__Clans__
<br>
**GET**             URL/clans
* Returns a user's clan
* params: none

**GET**             URL/clans/:tag
* Returns a specific clan with data directly from RoyaleAPI
* params: none

**POST**            URL/clans
* Adds a clan to the current user's account
* params: ```{tag: "clanTag"}```

**PUT**             URL/clans
* Fetches data from RoyaleAPI and replaces the user's clan data
* params: ```{tag: "clanTag"}```

**DELETE**          URL/clans/:id
* Deletes a clan in the database based on ID
* params: none

__Players__
<br>
