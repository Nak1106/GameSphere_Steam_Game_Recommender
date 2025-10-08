#!/usr/bin/env python3
"""
GameSphere Steam Recommender - Robust Data Cleaning Pipeline
Handles data quality issues and provides detailed logging
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, isnan, when, count, regexp_replace, lower, trim, isnotnull
from pyspark.sql.types import *
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_reviews(spark):
    """Clean raw Steam reviews data with robust error handling"""
    logger.info("Starting robust data cleaning pipeline...")
    
    try:
        # Read raw data from HDFS
        logger.info("Reading raw Steam reviews from HDFS...")
        raw_df = spark.read.option("header", "true").csv("hdfs:///project/raw/steam_reviews.csv")
        
        logger.info(f"Raw data loaded: {raw_df.count()} rows")
        logger.info("Schema:")
        raw_df.printSchema()
        
        # Show sample data to understand structure
        logger.info("Sample data (first 3 rows):")
        raw_df.show(3, truncate=False)
        
        # Check for required columns
        required_cols = ["review", "app_id", "language", "recommended"]
        available_cols = raw_df.columns
        logger.info(f"Available columns: {available_cols}")
        
        missing_cols = [col for col in required_cols if col not in available_cols]
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return None
            
        # Remove null values in critical columns - be more flexible
        logger.info("Filtering null values...")
        cleaned_df = raw_df.filter(
            col("review").isNotNull() & 
            col("app_id").isNotNull() & 
            col("language").isNotNull()
        )
        
        logger.info(f"After null removal: {cleaned_df.count()} rows")
        
        # Clean text data
        logger.info("Cleaning text data...")
        cleaned_df = cleaned_df.withColumn(
            "review_clean", 
            trim(regexp_replace(col("review"), r"[^\w\s]", ""))
        )
        
        # Filter for English reviews
        logger.info("Filtering for English reviews...")
        english_df = cleaned_df.filter(col("language") == "english")
        
        logger.info(f"English reviews: {english_df.count()} rows")
        
        # Create a simple, safe selection of columns
        logger.info("Selecting core columns...")
        final_df = english_df.select(
            col("app_id").cast("integer").alias("app_id"),
            col("review").alias("review_text"),
            col("review_clean"),
            col("recommended").cast("boolean").alias("recommended"),
            col("language")
        )
        
        # Show final schema
        logger.info("Final schema:")
        final_df.printSchema()
        
        logger.info("Sample of cleaned data:")
        final_df.show(5, truncate=True)
        
        # Write cleaned data to HDFS
        logger.info("Writing cleaned data to HDFS...")
        final_df.write \
            .mode("overwrite") \
            .parquet("hdfs:///project/processed/steam_reviews_cleaned.parquet")
        
        logger.info("✅ Data cleaning pipeline completed successfully!")
        logger.info(f"Final output: {final_df.count()} rows written to HDFS")
        
        return final_df
        
    except Exception as e:
        logger.error(f"❌ Error in data cleaning pipeline: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

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
