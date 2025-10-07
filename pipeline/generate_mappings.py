from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

spark = SparkSession.builder \
    .appName("Generate Mappings") \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://host.docker.internal:9000") \
    .getOrCreate()

df = spark.read.parquet("hdfs:///project/processed/steam_review_english.parquet")

games_mapping = df.select("app_id", "app_name").distinct() \
    .withColumn("app_index", row_number().over(Window.orderBy("app_id")) - 1)

author_mapping = df.select("author_steamid").distinct() \
    .withColumn("author_index", row_number().over(Window.orderBy("author_steamid")) - 1)

games_mapping.write.mode("overwrite").parquet("hdfs:///project/data/mappings/games_mapping.parquet")
author_mapping.write.mode("overwrite").parquet("hdfs:///project/data/mappings/author_mapping.parquet")

print("✅ Saved game and author mappings to HDFS.")

