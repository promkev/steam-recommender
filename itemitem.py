# %%
from pyspark.sql.functions import *
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.stat import Correlation
from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType

# %% Create a SparkSession
spark = SparkSession.builder.appName("GameMatrix").getOrCreate()

# %% Sample data
data = [("user1", "game1", 10), ("user2", "game2", 20), ("user1", "game2", 15), ("user2", "game1", 5), 
        ("user1", "game3", 30), ("user2", "game3", 25), ("user3", "game3", 15), ("user3", "game1", 10)]
df = spark.createDataFrame(data, ["steamid", "appid", "playtime_forever"])

# %% Create the game matrix
game_matrix = df.groupBy("appid").pivot("steamid").agg(first("playtime_forever"))
game_matrix.show()

# %% Replace null values with 0
for col in game_matrix.columns[1:]:
    game_matrix = game_matrix.withColumn(col, game_matrix[col].cast(DoubleType()))
    game_matrix = game_matrix.fillna(0.0, subset=[col])

# %% Extract columns with numerical values and assemble them into a vector column
numeric_cols = game_matrix.columns[1:]
assembler = VectorAssembler(inputCols=numeric_cols, outputCol="features")
vector_matrix = assembler.transform(game_matrix).select("features")

# %% Compute the Pearson correlation matrix between the rows
pearson_matrix = Correlation.corr(vector_matrix, "features", "pearson")

# %% Print the correlation array (numpy)
corr_array = pearson_matrix.head()[0].toArray()
print(corr_array)