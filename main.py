from pyspark.sql import SparkSession
from pyspark.rdd import RDD
from pyspark.sql import Row
from pyspark.sql import DataFrame
from pyspark.sql.window import Window  # for ranking
from pyspark.sql.functions import lit
from pyspark.sql.functions import collect_set, collect_list
from pyspark.sql.functions import struct
from pyspark.sql.functions import slice
from pyspark.sql.functions import col
from pyspark.sql.functions import desc
from pyspark.sql.functions import udf
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql.types import DecimalType, ArrayType, IntegerType, FloatType
import pyspark.sql.functions as F
from pyspark.sql.functions import avg, broadcast, when


# cosine similarity function
def cosine_similarity_udf(a, b):
    dot_product = sum([x * y for x, y in zip(a, b)])
    norm_a = sum([x**2 for x in a])**0.5
    norm_b = sum([x**2 for x in b])**0.5
    return dot_product / (norm_a * norm_b)


# weighted average features function
def weighted_avg_features(ratings, features):
    if not ratings or not features:
        return []

    weighted_sum = [0] * len(features[0])
    total_weight = 0

    for rating, feature in zip(ratings, features):
        weight = float(rating)
        total_weight += weight
        weighted_sum = [ws + weight * f for ws,
                        f in zip(weighted_sum, feature)]

    if total_weight == 0:
        return weighted_sum

    return [ws / total_weight for ws in weighted_sum]


spark = SparkSession.builder.appName('ReadMySQL') \
    .config("spark.driver.memory", "32g") \
    .config("spark.sql.pivotMaxValues", "1000000") \
    .config("spark.jars", "C:\\Program Files (x86)\\MySQL\\Connector J 8.0\\mysql-connector-j-8.0.32.jar") \
    .getOrCreate()

# sql = "select * from 01_sampled_games_2v2 WHERE playtime_forever IS NOT NULL AND playtime_forever > 0"
sql = """
SELECT p.steamid, p.appid, p.playtime_2weeks, p.playtime_forever, p.dateretrieved, g.genre
FROM 01_sampled_games_2v2 AS p
JOIN games_genres AS g ON p.appid = g.appid
WHERE p.playtime_forever IS NOT NULL AND p.playtime_forever > 0
"""
database = "steam"
user = "root"
password = "root"
server = "127.0.0.1"
port = 3307
jdbc_url = f"jdbc:mysql://{server}:{port}/{database}"
jdbc_driver = "com.mysql.cj.jdbc.Driver"

# Create a data frame by reading data from Oracle via JDBC
df = spark.read.format("jdbc") \
    .option("url", jdbc_url) \
    .option("query", sql) \
    .option("user", user) \
    .option("password", password) \
    .option("driver", jdbc_driver) \
    .load()

df.show(truncate=False)

# build the item profiles
# Group the data by 'appid' and collect the genres for each game into a list
games_genres_df = df.groupBy("appid").agg(collect_set("genre").alias("genres"))

# Create a list of unique genres
unique_genres = sorted(
    df.select("genre").distinct().rdd.flatMap(lambda x: x).collect())

# Define a UDF to create a binary vector for each game's genres


@udf(returnType=ArrayType(IntegerType()))
def genre_vector(genres):
    return [1 if genre in genres else 0 for genre in unique_genres]


# Add a new column 'genre_vector' to the DataFrame
# the genre vector will now have a 1 for each genre that the game belongs to
games_genres_df = games_genres_df.withColumn(
    "genre_vector", genre_vector("genres"))

# games_genres_df.show(truncate=False)
# Join the main DataFrame with the games_genres_df on appid to include the genre_vector
df = df.join(broadcast(games_genres_df.select(
    "appid", "genre_vector")), on="appid")

# build the user profiles

# 1. Calculate the global playtime average for each game
global_playtime_avg = df.groupBy("appid").agg(
    avg("playtime_forever").alias("global_playtime_avg"))

# 2. Normalize the user's playtime for each game based on the global average
df = df.join(broadcast(global_playtime_avg), on="appid")
df = df.withColumn("playtime_normalized", F.when(
    df.playtime_forever == 0, 1).otherwise(df.playtime_forever / df.global_playtime_avg))

# 3. Implement the user profile
# First, let's group the data by user and aggregate the genre vectors and normalized playtimes
user_aggregated_data = df.groupBy("steamid").agg(
    collect_list("genre_vector").alias("genres_list"),
    collect_list("playtime_normalized").alias("playtime_normalized_list")
)

# Now, let's define a UDF to calculate the weighted average of genre vectors
weighted_avg_features_udf = udf(weighted_avg_features, ArrayType(FloatType()))

# Calculate the user profile as the weighted average of rated item profiles (genre vectors)
user_profiles = user_aggregated_data.withColumn(
    "user_profile", weighted_avg_features_udf("playtime_normalized_list", "genres_list"))

# user_profiles.show(truncate=False)

# prediction heuristics
# calculate cosine distance of an item and user profile

# 1. create udf for cosine similarity
cosine_similarity = udf(cosine_similarity_udf, FloatType())
# cross join the game_genres_df with the user_profiles
cross_joined = games_genres_df.crossJoin(user_profiles)

# calculate the cosine similarity between each item and user
recommendations = cross_joined.withColumn(
    "similarity", cosine_similarity("genre_vector", "user_profile")
)

# sort based on similarity score
sorted_recommendations = recommendations.sort(desc("similarity"))

# sorted_recommendations.show(10)

# Create a window by steamid and similarity to get ranking
window_spec = Window.partitionBy("steamid").orderBy(desc("similarity"))

ranked_recommendations = sorted_recommendations.withColumn(
    "rank", F.row_number().over(window_spec))

top_10_recommendations = ranked_recommendations.filter(
    ranked_recommendations.rank <= 10)
top_10_recommendations.show(1)
