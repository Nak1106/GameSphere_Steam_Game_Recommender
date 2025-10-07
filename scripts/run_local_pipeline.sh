#!/bin/bash
# GameSphere Local Pipeline Runner
# Runs the entire pipeline locally without Docker

set -e

echo "🚀 Starting GameSphere Pipeline Locally..."

# Set environment variables
export JAVA_HOME=/opt/homebrew/opt/openjdk@11
export HADOOP_HOME=/Users/spartan/Hadoop/hadoop-3.4.1
export SPARK_HOME=/Users/spartan/Spark/spark-3.5.3/spark-3.5.3-bin-hadoop3

# Navigate to project directory
cd /Users/spartan/GameSphere_Steam_Game_Recommender

# Activate virtual environment
source .venv/bin/activate

echo "✅ Environment configured"
echo "   JAVA_HOME: $JAVA_HOME"
echo "   HADOOP_HOME: $HADOOP_HOME" 
echo "   SPARK_HOME: $SPARK_HOME"

# Check HDFS status
echo "🔍 Checking HDFS status..."
$HADOOP_HOME/bin/hdfs dfsadmin -report | head -10

# Run pipeline steps
echo "📊 Step 1: Data Cleaning..."
python pipeline/clean_reviews.py

echo "🤖 Step 2: Sentiment Analysis..."
python pipeline/run_sentiment.py

echo "🎯 Step 3: ALS Model Training..."
python pipeline/train_als.py

echo "📤 Step 4: Export Dashboard Data..."
python pipeline/export_dashboard_data.py

echo "🎉 Pipeline completed successfully!"
