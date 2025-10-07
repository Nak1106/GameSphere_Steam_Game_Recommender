#!/usr/bin/env python3
"""
GameSphere Steam Recommender - Data Cleaning Pipeline
Cleans raw Steam reviews and filters for English reviews
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, isnan, when, count, regexp_replace, lower, trim
from pyspark.sql.types import *
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Create Spark session with HDFS configuration"""
    return SparkSession.builder \
        .appName("GameSphere-DataCleaning") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://host.docker.internal:9000") \
        .config("spark.driver.bindAddress", "0.0.0.0") \
        .config("spark.sql.shuffle.partitions", "200") \
        .getOrCreate()

def clean_reviews(spark):
    """Clean raw Steam reviews data"""
    logger.info("Starting data cleaning pipeline...")
    
    # Read raw data from HDFS
    logger.info("Reading raw Steam reviews from HDFS...")
    raw_df = spark.read.option("header", "true").csv("hdfs:///project/raw/steam_reviews.csv")
    
    logger.info(f"Raw data count: {raw_df.count()}")
    
    # Data cleaning steps
    logger.info("Performing data cleaning...")
    
    # Remove null values in critical columns
    cleaned_df = raw_df.filter(
        col("review").isNotNull() & 
        col("app_id").isNotNull() & 
        col("author").isNotNull()
    )
    
    # Clean text data
    cleaned_df = cleaned_df.withColumn(
        "review_clean", 
        regexp_replace(trim(lower(col("review"))), r"[^\w\s]", " ")
    )
    
    # Filter for English reviews (basic heuristic - can be enhanced)
    # For now, we'll assume all reviews are English or use a simple filter
    english_df = cleaned_df.filter(col("language") == "english")
    
    # If language column doesn't exist, keep all reviews
    if "language" not in cleaned_df.columns:
        english_df = cleaned_df
    
    logger.info(f"Cleaned English reviews count: {english_df.count()}")
    
    # Write cleaned data to HDFS
    logger.info("Writing cleaned data to HDFS...")
    english_df.write \
        .mode("overwrite") \
        .parquet("hdfs:///project/processed/steam_review_english.parquet")
    
    logger.info("Data cleaning pipeline completed successfully!")

def main():
    spark = create_spark_session()
    try:
        clean_reviews(spark)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
