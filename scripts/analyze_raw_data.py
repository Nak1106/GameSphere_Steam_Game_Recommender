#!/usr/bin/env python3
"""
GameSphere Raw Data Analysis Script
Quick analysis of Steam reviews dataset to understand structure and quality
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, isnan, when, desc, avg, max as spark_max, min as spark_min
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Create Spark session with HDFS configuration"""
    return SparkSession.builder \
        .appName("GameSphere-DataAnalysis") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.sql.shuffle.partitions", "200") \
        .getOrCreate()

def analyze_raw_data(spark):
    """Analyze raw Steam reviews data"""
    logger.info("🔍 Starting GameSphere Raw Data Analysis...")
    
    # Read raw data from HDFS
    logger.info("📊 Loading raw Steam reviews from HDFS...")
    raw_df = spark.read.option("header", "true").csv("hdfs:///project/raw/steam_reviews.csv")
    
    print("=" * 80)
    print("🎮 GAMESPHERE RAW DATA ANALYSIS REPORT")
    print("=" * 80)
    
    # Basic statistics
    total_records = raw_df.count()
    print(f"\n📈 DATASET OVERVIEW:")
    print(f"   Total Records: {total_records:,}")
    print(f"   Total Columns: {len(raw_df.columns)}")
    
    # Schema information
    print(f"\n📋 SCHEMA ANALYSIS:")
    for field in raw_df.schema.fields:
        print(f"   {field.name:<30} | {field.dataType}")
    
    # Language distribution
    print(f"\n🌍 LANGUAGE DISTRIBUTION:")
    language_dist = raw_df.groupBy("language").count().orderBy(desc("count")).limit(10)
    language_results = language_dist.collect()
    
    total_with_lang = sum(row['count'] for row in language_results)
    for row in language_results:
        percentage = (row['count'] / total_with_lang) * 100
        lang_name = row['language'] if row['language'] is not None else 'NULL'
        print(f"   {lang_name:<15} | {row['count']:>10,} ({percentage:5.1f}%)")
    
    # English reviews analysis
    english_df = raw_df.filter(col("language") == "english")
    english_count = english_df.count()
    english_percentage = (english_count / total_records) * 100
    
    print(f"\n🇺🇸 ENGLISH REVIEWS ANALYSIS:")
    print(f"   English Reviews: {english_count:,} ({english_percentage:.1f}% of total)")
    
    # Data quality analysis
    print(f"\n🔍 DATA QUALITY ANALYSIS:")
    
    # Check for null values in critical columns
    critical_columns = ["app_id", "review", "author.steamid", "recommended"]
    for col_name in critical_columns:
        if col_name in raw_df.columns:
            null_count = raw_df.filter(col(col_name).isNull()).count()
            null_percentage = (null_count / total_records) * 100
            print(f"   {col_name:<20} | Nulls: {null_count:>8,} ({null_percentage:5.2f}%)")
    
    # Review length analysis (for English reviews)
    print(f"\n📝 REVIEW TEXT ANALYSIS (English only):")
    english_with_length = english_df.withColumn("review_length", 
                                               when(col("review").isNotNull(), 
                                                   col("review").cast("string").length()).otherwise(0))
    
    length_stats = english_with_length.agg(
        avg("review_length").alias("avg_length"),
        spark_min("review_length").alias("min_length"),
        spark_max("review_length").alias("max_length")
    ).collect()[0]
    
    print(f"   Average Length: {length_stats['avg_length']:.0f} characters")
    print(f"   Min Length:     {length_stats['min_length']} characters")
    print(f"   Max Length:     {length_stats['max_length']:,} characters")
    
    # Game popularity analysis
    print(f"\n🎯 GAME POPULARITY ANALYSIS:")
    game_stats = raw_df.groupBy("app_id", "app_name").count().orderBy(desc("count")).limit(10)
    game_results = game_stats.collect()
    
    print("   Top 10 Most Reviewed Games:")
    for i, row in enumerate(game_results, 1):
        game_name = row['app_name'][:40] + "..." if len(row['app_name']) > 40 else row['app_name']
        print(f"   {i:2d}. {game_name:<43} | {row['count']:>8,} reviews")
    
    # Recommendation distribution
    print(f"\n👍 RECOMMENDATION ANALYSIS:")
    rec_dist = raw_df.groupBy("recommended").count().collect()
    for row in rec_dist:
        if row['recommended'] is not None:
            percentage = (row['count'] / total_records) * 100
            rec_label = "Positive" if row['recommended'] else "Negative"
            print(f"   {rec_label:<12} | {row['count']:>10,} ({percentage:5.1f}%)")
    
    # User activity analysis
    print(f"\n👤 USER ACTIVITY ANALYSIS:")
    user_stats = raw_df.groupBy("author.steamid").count().agg(
        avg("count").alias("avg_reviews_per_user"),
        spark_max("count").alias("max_reviews_per_user")
    ).collect()[0]
    
    unique_users = raw_df.select("author.steamid").distinct().count()
    print(f"   Unique Users:           {unique_users:,}")
    print(f"   Avg Reviews per User:   {user_stats['avg_reviews_per_user']:.1f}")
    print(f"   Max Reviews per User:   {user_stats['max_reviews_per_user']:,}")
    
    # Preprocessing readiness assessment
    print(f"\n✅ PREPROCESSING READINESS ASSESSMENT:")
    
    # Calculate expected output sizes
    expected_english = english_count
    expected_games = raw_df.select("app_id").distinct().count()
    expected_users = unique_users
    
    print(f"   Expected English Reviews:     {expected_english:,}")
    print(f"   Expected Unique Games:        {expected_games:,}")
    print(f"   Expected Unique Users:        {expected_users:,}")
    print(f"   Expected Processing Time:     ~3.5 hours")
    print(f"   Expected Output Size:         ~5GB")
    
    # Data quality score
    null_score = 100 - (sum(raw_df.filter(col(c).isNull()).count() for c in critical_columns) / (total_records * len(critical_columns))) * 100
    english_score = english_percentage
    overall_score = (null_score + english_score) / 2
    
    print(f"\n🏆 DATA QUALITY SCORE:")
    print(f"   Completeness Score:     {null_score:.1f}%")
    print(f"   English Coverage:       {english_score:.1f}%")
    print(f"   Overall Quality:        {overall_score:.1f}%")
    
    if overall_score >= 80:
        print("   Status: ✅ EXCELLENT - Ready for processing")
    elif overall_score >= 60:
        print("   Status: ⚠️  GOOD - Minor issues, proceed with caution")
    else:
        print("   Status: ❌ POOR - Significant data quality issues")
    
    print("\n" + "=" * 80)
    print("📊 Analysis Complete! Data is ready for preprocessing pipeline.")
    print("=" * 80)

def main():
    spark = create_spark_session()
    try:
        analyze_raw_data(spark)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
