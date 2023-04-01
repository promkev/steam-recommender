```sql
CREATE TABLE sampled_games_2 AS
SELECT *
FROM (
  SELECT *
  FROM Games_2
  WHERE steamid % 50 = 0 -- This selects 2% of users
) AS sampled

SELECT COUNT(DISTINCT steamid) AS unique_users
FROM sampled_games_2;

CREATE TABLE 01_sampled_games_2 AS
SELECT *
FROM (
  SELECT *
  FROM Games_2
  WHERE steamid % 1000 = 0 -- This selects 0.1% of users
) AS sampled;


CREATE TABLE 01_sampled_games_2v2 AS
SELECT *
FROM (
  SELECT *
  FROM 01_sampled_games_2
  WHERE appid % 10 = 0 -- This selects 0.1% of users
) AS sampled;

CREATE TABLE 01_sampled_games_2v2v2 AS
SELECT * FROM 01_sampled_games_2v2;


SELECT 
  t.steamid,
  t.appid,
  t.playtime_2weeks,
  (t.playtime_forever - g.mean_playtime) AS adjusted_playtime_forever,
  t.dateretrieved
FROM 01_sampled_games_2v2v2 t
JOIN (
  SELECT appid, AVG(playtime_forever) AS mean_playtime
  FROM 01_sampled_games_2v2v2
  WHERE playtime_forever IS NOT NULL
  GROUP BY appid
) g
ON t.appid = g.appid
WHERE t.playtime_forever IS NOT NULL;

```