# ClashClanTracker - 
#### A web API used for gathering and storing clan and player data from Clash Royale
<hr>

## Routes
URL = https://clashclantracker.appspot.com

## __Users__
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


## __Clans__
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

## __Players__
<br>
**GET**             URL/players/:player_id
* Returns player data based on player_id. Either you can use the database ID to return your player's info from the database, or you can use a game tag to fetch data from RoyaleAPI
* params: none

**GET**            URL/players
* Returns all players in the database
* params: none

**POST**           URL/players
* Adds a player to the database based on player tag
* params: ```{tag: "playerTag"}```

**PUT**             URL/players/:player_id
* Fetches player data from RoyaleAPI and replaces the database entry with new data
* params: ```{tag: "playerTag"}```

**DEL**             URL/players/:player_id
* Deletes a player from database based on id
* params: none
