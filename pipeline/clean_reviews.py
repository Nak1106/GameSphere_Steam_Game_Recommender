from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# ✅ Start Spark Session with HDFS config
spark = SparkSession.builder \
    .appName("SteamReviewsHDFS") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "4g") \
    .config("spark.sql.shuffle.partitions", "100") \
    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
    .getOrCreate()

# ✅ Load raw CSV from HDFS
print("📥 Loading CSV from HDFS...")
df = spark.read.csv("hdfs://localhost:9000/project/raw/steam_reviews.csv", header=True, inferSchema=True)

# ✅ Debug raw data
print("✅ Raw DataFrame loaded")
df.printSchema()
print("✅ Row count before cleaning:", df.count())

# ✅ Rename nested fields for Spark compatibility
data_csv = df.withColumnRenamed("author.steamid", "author_steamid") \
             .withColumnRenamed("author.num_games_owned", "author_num_games_owned") \
             .withColumnRenamed("author.num_reviews", "author_num_reviews") \
             .withColumnRenamed("author.playtime_forever", "author_playtime_forever") \
             .withColumnRenamed("author.playtime_at_review", "author_playtime_at_review") \
             .withColumnRenamed("author.last_played", "author_last_played") \
             .withColumnRenamed("author.playtime_last_two_weeks", "author_playtime_last_two_weeks")

# ✅ Handle missing values
important_cols = ["app_id", "app_name", "review_id", "review", "recommended", "author_steamid"]
numeric_fill_cols = ["votes_helpful", "votes_funny", "comment_count", "weighted_vote_score"]

# Drop rows missing important fields
df_clean = data_csv.dropna(subset=important_cols)

# Fill missing numeric columns with 0
for col_name in numeric_fill_cols:
    df_clean = df_clean.withColumn(col_name, coalesce(col(col_name), lit(0)))

# Fill unknown for some categorical fields
df_clean = df_clean.fillna({
    "steam_purchase": "unknown",
    "received_for_free": "unknown"
})

# ✅ Normalize text (HTML, emojis, non-letter symbols)
df_clean = df_clean.withColumn(
    "cleaned_review",
    regexp_replace(lower(col("review")), "<[^>]*>", "")
)
df_clean = df_clean.withColumn(
    "cleaned_review",
    regexp_replace(col("cleaned_review"), "[^\\p{L}\\s]", "")
)
df_clean = df_clean.withColumn("cleaned_review", trim(col("cleaned_review")))

# ✅ Filter English only
df_clean = df_clean.filter(col("language") == "english")

# ✅ Show schema + cleaned row count
print("✅ Cleaned DataFrame schema:")
df_clean.printSchema()
print("✅ Cleaned row count:", df_clean.count())

# ✅ Save cleaned reviews to HDFS
try:
    df_clean.write.mode("overwrite").parquet("hdfs://localhost:9000/project/processed/steam_review_english.parquet")
    print("✅ Data cleaning complete. Cleaned reviews saved to HDFS.")
except Exception as e:
    print("❌ Error while writing Parquet:", str(e))
