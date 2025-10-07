#!/usr/bin/env python3
"""
GameSphere Steam Recommender - ALS Model Training Pipeline
Trains collaborative filtering model using Spark MLlib ALS
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, isnan, count, desc
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import StringIndexer
import logging
import mlflow
import mlflow.spark

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Create Spark session with HDFS configuration"""
    return SparkSession.builder \
        .appName("GameSphere-ALSTraining") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://host.docker.internal:9000") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.sql.shuffle.partitions", "200") \
        .getOrCreate()

def prepare_rating_data(spark):
    """Prepare rating data from cleaned reviews"""
    logger.info("Preparing rating data for ALS training...")
    
    # Read cleaned reviews
    reviews_df = spark.read.parquet("hdfs:///project/processed/steam_review_english.parquet")
    
    # Create implicit ratings based on review sentiment/recommendation
    # Assume we have a 'recommended' column (True/False) or create from sentiment
    if "recommended" in reviews_df.columns:
        ratings_df = reviews_df.select("author", "app_id", "recommended") \
            .withColumn("rating", when(col("recommended") == True, 1.0).otherwise(0.0))
    else:
        # Create ratings from review length and assume positive sentiment
        ratings_df = reviews_df.select("author", "app_id") \
            .withColumn("rating", 1.0)  # Implicit positive rating
    
    # Index string columns to numeric for ALS
    author_indexer = StringIndexer(inputCol="author", outputCol="author_index")
    app_indexer = StringIndexer(inputCol="app_id", outputCol="app_index")
    
    ratings_indexed = author_indexer.fit(ratings_df).transform(ratings_df)
    ratings_indexed = app_indexer.fit(ratings_indexed).transform(ratings_indexed)
    
    # Select final columns for ALS
    final_ratings = ratings_indexed.select("author_index", "app_index", "rating") \
        .withColumnRenamed("author_index", "user") \
        .withColumnRenamed("app_index", "item")
    
    logger.info(f"Prepared {final_ratings.count()} ratings for training")
    return final_ratings, author_indexer, app_indexer

def train_als_model(spark):
    """Train ALS collaborative filtering model"""
    logger.info("Starting ALS model training...")
    
    with mlflow.start_run(run_name="als_training"):
        # Prepare data
        ratings_df, author_indexer, app_indexer = prepare_rating_data(spark)
        
        # Split data for training and validation
        train_df, test_df = ratings_df.randomSplit([0.8, 0.2], seed=42)
        
        # Configure ALS parameters
        rank = 10
        max_iter = 10
        reg_param = 0.1
        
        mlflow.log_param("rank", rank)
        mlflow.log_param("max_iter", max_iter)
        mlflow.log_param("reg_param", reg_param)
        
        # Initialize and train ALS model
        logger.info("Training ALS model...")
        als = ALS(
            rank=rank,
            maxIter=max_iter,
            regParam=reg_param,
            userCol="user",
            itemCol="item",
            ratingCol="rating",
            coldStartStrategy="drop",
            implicitPrefs=True  # For implicit feedback
        )
        
        model = als.fit(train_df)
        
        # Generate predictions on test set
        logger.info("Evaluating model...")
        predictions = model.transform(test_df)
        
        # Evaluate model performance
        evaluator = RegressionEvaluator(
            metricName="rmse",
            labelCol="rating",
            predictionCol="prediction"
        )
        
        rmse = evaluator.evaluate(predictions.filter(~isnan(col("prediction"))))
        logger.info(f"Model RMSE: {rmse:.4f}")
        
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("training_samples", train_df.count())
        mlflow.log_metric("test_samples", test_df.count())
        
        # Generate recommendations for all users
        logger.info("Generating recommendations...")
        user_recs = model.recommendForAllUsers(10)  # Top 10 recommendations per user
        
        # Save model and recommendations
        logger.info("Saving model and recommendations...")
        
        # Save the trained model
        model.write().overwrite().save("hdfs:///project/outputs/als_model")
        
        # Save user recommendations
        user_recs.write \
            .mode("overwrite") \
            .parquet("hdfs:///project/outputs/user_recommendations.parquet")
        
        # Log model to MLflow
        mlflow.spark.log_model(model, "als_model")
        
        logger.info("ALS model training completed successfully!")
        return model

def main():
    spark = create_spark_session()
    try:
        train_als_model(spark)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
