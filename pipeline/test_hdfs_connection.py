#!/usr/bin/env python3
"""
Simple test script to verify HDFS connectivity from Docker
"""

from pyspark.sql import SparkSession
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test HDFS connection"""
    logger.info("Starting HDFS connection test...")
    
    # Get or create SparkSession (works with spark-submit)
    spark = SparkSession.builder.getOrCreate()
    
    try:
        # Test HDFS connection by listing files
        logger.info("Testing HDFS connection...")
        
        # Try to read the raw data file
        logger.info("Attempting to read steam_reviews.csv from HDFS...")
        df = spark.read.option("header", "true").csv("hdfs:///project/raw/steam_reviews.csv")
        
        # Get basic info
        count = df.count()
        logger.info(f"✅ SUCCESS: Read {count} rows from HDFS!")
        
        # Show schema
        logger.info("Schema:")
        df.printSchema()
        
        # Show first few rows
        logger.info("First 5 rows:")
        df.show(5, truncate=False)
        
        logger.info("🎉 HDFS connection test completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ HDFS connection test failed: {str(e)}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
