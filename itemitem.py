# %%
from pyspark.sql.functions import *
from pyspark.sql import SparkSession

# %%

# Create a SparkSession
spark = SparkSession.builder.appName("GameMatrix").getOrCreate()

# %%
# Create a sample DataFrame with some data
data = [("user1", "game1", 10), ("user2", "game2", 20), ("user1", "game2", 15), ("user2", "game1", 5)]
df = spark.createDataFrame(data, ["steamid", "appid", "playtime_forever"])

# %%
# Use groupBy and pivot to create the matrix
game_matrix = df.groupBy("appid").pivot("steamid").agg(first("playtime_forever"))

# %%
# Show the resulting matrix
game_matrix.show()