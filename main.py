from pyspark.sql import SparkSession
from pyspark.rdd import RDD
from pyspark.sql import Row
from pyspark.sql import DataFrame
from pyspark.sql.functions import lit
from pyspark.sql.functions import desc
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql.types import DecimalType

spark = SparkSession.builder.appName('ReadMariaDB') \
.config("spark.driver.memory", "32g") \
.config("spark.sql.pivotMaxValues", "1000000") \
.getOrCreate()


sql = "select * from 01_sampled_games_2v2 WHERE playtime_forever IS NOT NULL AND playtime_forever > 0"
database = "steam"
user = "root"
password = "example"
server = "127.0.0.1"
port = 3306
jdbc_url = f"jdbc:mysql://{server}:{port}/{database}?permitMysqlScheme"
jdbc_driver = "org.mariadb.jdbc.Driver"

# Create a data frame by reading data from Oracle via JDBC
df = spark.read.format("jdbc") \
    .option("url", jdbc_url) \
    .option("query", sql) \
    .option("user", user) \
    .option("password", password) \
    .option("driver", jdbc_driver) \
    .load()

df.show()


ratingsRDD = df.map(lambda p: Row(steamId=int(p[0]), appId=int(p[1]), rating=DecimalType(p[2])))

ratings = spark.createDataFrame(ratingsRDD)
(training, test) = ratings.randomSplit([0.8, 0.2], seed=123)

als = ALS(maxIter=5, rank=70, regParam=0.01, coldStartStrategy='drop', userCol='steamId', itemCol='appId', ratingCol='rating', implicitPrefs=True)
als.setSeed(123)
model = als.fit(training)

predictions = model.transform(test)
evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction")
rmse = evaluator.evaluate(predictions)

print(rmse)