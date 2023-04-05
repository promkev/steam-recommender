# Steam Game Recommender
Steam is an online platform used by most video game publishers for PC game distribution. User purchase and playtime data are recorded and are available publicly by default. Game recommenders are therefore important tools for game discovery. The Steam Game Recommender utilizes part of a 170GB dataset that was scraped from the Steam API and stems into two recommendation models. First, a content-based filtering approach where users are matched to unplayed games that have similar features to games they have significant playtime in. Second, a item-item collaborative filtering approach where unplayed game playtime are estimated from the user’s playtime on games weighted by similarity. The top unplayed games are then used as recommendations.

## Research Questions

* Does a user's playtime as implicit ratings properly represent their game preferences when used in a recommender system?
* How can additional game metadata(e.g. publisher, developer, release date) beyond game genre(s) improve content-based filtering recommendations (i.e. rating estimation accuracy)?

## Dataset
* Source: https://steam.internet.byu.edu/
* 109 million users
* 716 million games

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
* release_date: the date when the game was first made available on the Steam storefront.

## Per-Game 1-5 Rating Normalization
For each game, we calculate the mean and standard deviation. We then create buckets for each rating:
### Scaling factor
The cut points are scaled on a per-user basis since some users are more casual gamers while others may spend a lot more time gaming. The scaling factor is calculated as follows:

(user_playtime_average)/(global_playtime_average)

### Cut points
* Cut point 1: (mean - std_dev*0.5) * scaling_factor if > 0, else 0
* Cut point 2: mean
* Cut point 3: (mean + std_dev*0.5) * scaling_factor
* Cut point 4: (mean + std_dev) * scaling_factor
### Ratings
* Rating 1: 0 < x < cut point 1
* Rating 2: cut point 1 < x < cut point 2
* Rating 3: cut point 2 < x < cut point 3
* Rating 4: cut point 3 < x < cut point 4
* Rating 5: cut point 5 < x < inf

## Models
### Content-based filtering model
#### Algorithm
1. Build the item profiles: vector of the game’s genre, developer and publisher from the dataset.
    ![image](https://user-images.githubusercontent.com/67298240/220737000-6543b02a-91e9-4b8d-832c-f341d9c09392.png)
2. Build the user profile: weighted average of rated item profiles.
    ![image](https://user-images.githubusercontent.com/67298240/220737101-2dea36d6-896a-4052-ba7a-1d4c54c3fc7f.png)
3. Prediction heuristics: cosine distance of an item and user profile.
    ![image](https://user-images.githubusercontent.com/67298240/220737309-457ac254-d4b5-4c9c-85e1-4b9c26adaa3a.png)
4. Recommend top N games by estimated ratings

### Item-item collaborative filtering model
#### Algorithm
User by game rating matrix

![image](https://user-images.githubusercontent.com/51273366/220733175-ab374386-6fef-425c-af60-abc3922fd977.png)
1. Compute estimated ratings for all games that user x has not played:
    1. Use cosine similarity to define similarities to unplayed game i
    2. Obtain KNNs of unplayed game i and estimate rating through the average weighted by similarities
2. Recommend top N games by estimated ratings


