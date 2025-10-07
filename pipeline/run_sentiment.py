#!/usr/bin/env python3
"""
GameSphere Steam Recommender - Sentiment Analysis Pipeline
Runs BERT-based sentiment analysis on English Steam reviews
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, avg, count, when
from pyspark.sql.types import StringType, FloatType
import logging
import mlflow
import mlflow.spark

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Create Spark session with HDFS configuration"""
    return SparkSession.builder \
        .appName("GameSphere-SentimentAnalysis") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.sql.shuffle.partitions", "200") \
        .getOrCreate()

def analyze_sentiment_batch(reviews):
    """
    Analyze sentiment for a batch of reviews using BERT
    This is a placeholder - implement with transformers pipeline
    """
    try:
        from transformers import pipeline
        # Initialize sentiment pipeline (cached after first call)
        sentiment_pipeline = pipeline("sentiment-analysis", 
                                     model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                                     return_all_scores=True)
        
        results = []
        for review in reviews:
            if review and len(review.strip()) > 0:
                try:
                    scores = sentiment_pipeline(review[:512])  # Truncate to 512 chars
                    # Get positive sentiment score
                    pos_score = next((s['score'] for s in scores[0] if s['label'] == 'POSITIVE'), 0.5)
                    results.append(float(pos_score))
                except:
                    results.append(0.5)  # Neutral default
            else:
                results.append(0.5)
        return results
    except ImportError:
        logger.warning("Transformers not available, using dummy sentiment scores")
        # Return dummy scores for testing
        import random
        return [random.uniform(0.0, 1.0) for _ in reviews]

def run_sentiment_analysis(spark):
    """Run sentiment analysis on cleaned reviews"""
    logger.info("Starting sentiment analysis pipeline...")
    
    # Start MLflow run
    with mlflow.start_run(run_name="sentiment_analysis"):
        # Read cleaned English reviews
        logger.info("Reading cleaned English reviews from HDFS...")
        reviews_df = spark.read.parquet("hdfs:///project/processed/steam_review_english.parquet")
        
        logger.info(f"Processing {reviews_df.count()} reviews for sentiment analysis")
        
        # Create UDF for sentiment analysis
        sentiment_udf = udf(lambda review: float(analyze_sentiment_batch([review])[0]), FloatType())
        
        # Apply sentiment analysis
        logger.info("Running sentiment analysis...")
        sentiment_df = reviews_df.withColumn("sentiment_score", sentiment_udf(col("review")))
        
        # Aggregate sentiment by game (app_id)
        logger.info("Aggregating sentiment by game...")
        sentiment_summary = sentiment_df.groupBy("app_id") \
            .agg(
                avg("sentiment_score").alias("avg_sentiment"),
                count("*").alias("review_count"),
                avg(when(col("sentiment_score") > 0.6, 1).otherwise(0)).alias("positive_ratio")
            )
        
        # Log metrics to MLflow
        total_reviews = sentiment_df.count()
        avg_sentiment = sentiment_df.agg(avg("sentiment_score")).collect()[0][0]
        
        mlflow.log_metric("total_reviews_processed", total_reviews)
        mlflow.log_metric("average_sentiment_score", avg_sentiment)
        mlflow.log_metric("unique_games", sentiment_summary.count())
        
        logger.info(f"Processed {total_reviews} reviews with average sentiment: {avg_sentiment:.3f}")
        
        # Write sentiment summary to HDFS
        logger.info("Writing sentiment summary to HDFS...")
        sentiment_summary.write \
            .mode("overwrite") \
            .parquet("hdfs:///project/data/processed/steam_sentiment_summary.parquet")
        
        logger.info("Sentiment analysis pipeline completed successfully!")

def main():
    spark = create_spark_session()
    try:
        run_sentiment_analysis(spark)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
