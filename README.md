# Steam Game Recommender
Steam is an online platform used by most video game publishers for PC game distribution. User purchase and playtime data are recorded and are available publicly by default. Game recommenders are therefore important tools for game discovery. The Steam Game Recommender utilizes part of a 170GB dataset that was scraped from the Steam API and stems into two recommendation models. First, a content-based filtering approach where users are matched to unplayed games that have similar features to games they have significant playtime in. Second, a item-item collaborative filtering approach where unplayed game playtime are estimated from the user’s playtime on games weighted by similarity. The top unplayed games are then used as recommendations.

## Research Questions

* How does the rating prediction accuracy differ between the content-based filtering and item-item collaborative filtering models? 
* How can game metadata(e.g. publisher, developer, release date) beyond game genre(s) improve content-based filtering recommendations?

## Models
### Playtime normalization
For both models, game ratings will be obtained by normalizing the total playtime of users for each individual game. Normalization is per game since a short story game may be finished in a few hours while RPG genre games may be played for hundreds of hours. In addition, games with zero playtime will be considered as average in the ratings. Normalization would be {game X playtime for user A}/{game X global playtime average} and 0 playtime being normalized to {game X global playtime average}.

### Content-based filtering model
#### Algorithm
1. Build the item profiles: vector of the game’s genre, developer and publisher from the dataset.
![image](https://user-images.githubusercontent.com/67298240/220737000-6543b02a-91e9-4b8d-832c-f341d9c09392.png)
2. Build the user profile: weighted average of rated item profiles.
![image](https://user-images.githubusercontent.com/67298240/220737101-2dea36d6-896a-4052-ba7a-1d4c54c3fc7f.png)
3. Prediction heuristics: cosine distance of an item and user profile.
![image](https://user-images.githubusercontent.com/67298240/220737309-457ac254-d4b5-4c9c-85e1-4b9c26adaa3a.png)
4. Recommend top N games

### Item-item collaborative filtering model
#### Algorithm
![image](https://user-images.githubusercontent.com/51273366/220733175-ab374386-6fef-425c-af60-abc3922fd977.png)
1. Compute estimated ratings for all games that user x has not played:
    1. Use cosine similarity to define similarities to unplayed game i
    2. Obtain KNNs of unplayed game i and estimate rating through the average weighted by similarities
2. Recommend top N games

## Dataset
Source: https://steam.internet.byu.edu/

### Users_Games
One row per user per purchased game.
* steamid: a unique identifier for a user.
* appid: a unique identifier for a game.
* playtime_forever: total time the user has played the game in minutes.
### Games
One row per game.
* appid: a unique identifier for a game.
* genre: the name of genre associated with the game (multiple possible)
* developer: the name of the game’s developer (multiple possible)
* publisher: the name of the game’s publisher (multiple possible)
* rating? The rating of the "app" on Metacritic. Set to -1 if not applicable.
