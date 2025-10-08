#!/usr/bin/env python3
"""
GameSphere Steam Recommender - Data Cleaning Pipeline (Docker Version)
Cleans raw Steam reviews and filters for English reviews
Designed to work with spark-submit from Airflow
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, isnan, when, count, regexp_replace, lower, trim
from pyspark.sql.types import *
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_reviews(spark):
    """Clean raw Steam reviews data"""
    logger.info("Starting data cleaning pipeline...")
    
    # Read raw data from HDFS (using host.docker.internal for Docker)
    logger.info("Reading raw Steam reviews from HDFS...")
    raw_df = spark.read.option("header", "true").csv("hdfs:///project/raw/steam_reviews.csv")
    
    logger.info(f"Raw data loaded: {raw_df.count()} rows")
    
    # Remove null values in critical columns
    cleaned_df = raw_df.filter(
        col("review").isNotNull() & 
        col("app_id").isNotNull() & 
        col("`author.steamid`").isNotNull()
    )
    
    logger.info(f"After null removal: {cleaned_df.count()} rows")
    
    # Clean text data
    cleaned_df = cleaned_df.withColumn(
        "review_clean", 
        trim(regexp_replace(col("review"), r"[^\w\s]", ""))
    )
    
    # Filter for English reviews (basic heuristic)
    english_df = cleaned_df.filter(col("language") == "english")
    
    logger.info(f"English reviews: {english_df.count()} rows")
    
    # Select relevant columns
    final_df = english_df.select(
        col("app_id").cast("integer"),
        col("`author.steamid`").alias("user_id"),
        col("review").alias("review_text"),
        col("review_clean"),
        col("recommended").cast("boolean").alias("recommended"),
        col("votes_helpful").cast("integer"),
        col("votes_funny").cast("integer"),
        col("weighted_vote_score").cast("double"),
        col("comment_count").cast("integer"),
        col("steam_purchase").cast("boolean"),
        col("received_for_free").cast("boolean"),
        col("written_during_early_access").cast("boolean"),
        col("`author.num_games_owned`").cast("integer").alias("user_games_owned"),
        col("`author.num_reviews`").cast("integer").alias("user_reviews_count"),
        col("`author.playtime_forever`").cast("integer").alias("playtime_forever"),
        col("`author.playtime_last_two_weeks`").cast("integer").alias("playtime_recent"),
        col("`author.playtime_at_review`").cast("integer").alias("playtime_at_review"),
        col("`author.last_played`").cast("long").alias("last_played_timestamp")
    )
    
    # Write cleaned data to HDFS
    logger.info("Writing cleaned data to HDFS...")
    final_df.write \
        .mode("overwrite") \
        .parquet("hdfs:///project/processed/steam_reviews_cleaned.parquet")
    
    logger.info("Data cleaning pipeline completed successfully!")
    
    return final_df

def main():
    """Main function for standalone execution"""
    # Get or create SparkSession (works with spark-submit)
    spark = SparkSession.builder.getOrCreate()
    
    try:
        clean_reviews(spark)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
