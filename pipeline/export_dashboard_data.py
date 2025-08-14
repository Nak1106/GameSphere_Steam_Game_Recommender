from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, col

# Start Spark
spark = SparkSession.builder \
    .appName("Prepare Dashboard Data") \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
    .getOrCreate()

# Load HDFS files
recommendations_df = spark.read.parquet("hdfs:///project/outputs/app_recommendations.parquet")
games_df = spark.read.parquet("hdfs:///project/data/mappings/games_mapping.parquet")
sentiment_summary = spark.read.parquet("hdfs:///project/data/processed/steam_sentiment_summary.parquet")

# Explode ALS recommendations
exploded_recs = recommendations_df.withColumn("rec", explode("recommendations")) \
    .select(
        col("author_index"),
        col("rec.app_index").alias("app_index"),
        col("rec.rating").alias("predicted_rating")
    )

# Join app names and sentiment summary
full_recs = exploded_recs.join(games_df, on="app_index", how="inner")

final_df = full_recs.join(
    sentiment_summary,
    full_recs.app_name == sentiment_summary.app_name,
    "left"
).select(
    full_recs["author_index"],
    full_recs["app_name"],
    "predicted_rating",
    "avg_sentiment_score",
    "positive_reviews",
    "negative_reviews",
    "percent_positive",
    "percent_negative"
)

# 🔍 Debug output
print("🔎 Row count:", final_df.count())
final_df.show(5, truncate=False)

# ✅ Export to local .parquet file
final_df.write.mode("overwrite").parquet("file:///Users/ayushkumbhani/Documents/Nakshatra/Project/gamesphere/final_recommendations.parquet")

print("✅ Saved final_recommendations.parquet to local disk.")
