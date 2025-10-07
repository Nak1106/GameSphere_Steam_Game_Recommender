from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, when, sum
from pyspark.sql.types import IntegerType

# ✅ Start Spark session
spark = SparkSession.builder \
    .appName("Sentiment Summary Aggregator") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://host.docker.internal:9000") \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .getOrCreate()

# ✅ Load local sentiment-labeled Parquet
df = spark.read.parquet("file:///Users/ayushkumbhani/Documents/Nakshatra/Project/gamesphere/data/outputs/steam_sentiment_final_batched.parquet")

# ✅ Create numeric label column
df = df.withColumn("is_positive", when(col("sentiment_label") == "POSITIVE", 1).otherwise(0).cast(IntegerType()))

# ✅ Aggregate sentiment data per game
summary = df.groupBy("app_id", "app_name").agg(
    avg("sentiment_score").alias("avg_sentiment_score"),
    count("*").alias("total_reviews"),
    sum("is_positive").alias("positive_reviews")
)

# ✅ Derive additional stats
summary = summary.withColumn("negative_reviews", col("total_reviews") - col("positive_reviews"))
summary = summary.withColumn("percent_positive", (col("positive_reviews") / col("total_reviews")) * 100)
summary = summary.withColumn("percent_negative", (col("negative_reviews") / col("total_reviews")) * 100)

# ✅ Save result to HDFS
summary.write.mode("overwrite").parquet("hdfs:///project/data/processed/steam_sentiment_summary.parquet")

print("✅ Sentiment summary saved to HDFS.")
