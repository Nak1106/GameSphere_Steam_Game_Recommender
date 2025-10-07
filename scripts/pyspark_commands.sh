#!/bin/bash

# GameSphere PySpark Commands Reference
# All essential PySpark commands for data processing and ML

# =============================================================================
# PYSPARK ENVIRONMENT SETUP
# =============================================================================

echo "=== PySpark Environment Setup ==="
echo "Set environment variables:"
echo "  export SPARK_HOME=~/Spark/spark-3.5.3"
echo "  export PYSPARK_PYTHON=python3"
echo "  export JAVA_HOME=/opt/homebrew/opt/openjdk@11"
echo ""

echo "Activate Python environment:"
echo "  source .venv/bin/activate"
echo ""

echo "Start PySpark shell:"
echo "  pyspark --conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000"
echo ""

echo "Start PySpark with specific configuration:"
echo "  pyspark \\"
echo "    --master local[*] \\"
echo "    --conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 \\"
echo "    --conf spark.driver.bindAddress=127.0.0.1 \\"
echo "    --conf spark.sql.shuffle.partitions=200"
echo ""

# =============================================================================
# SPARK SUBMIT COMMANDS
# =============================================================================

echo "=== Spark Submit Commands ==="
echo "Run data cleaning pipeline:"
echo "  spark-submit \\"
echo "    --master local[*] \\"
echo "    --conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 \\"
echo "    --conf spark.driver.bindAddress=127.0.0.1 \\"
echo "    --conf spark.sql.shuffle.partitions=200 \\"
echo "    pipeline/clean_reviews.py"
echo ""

echo "Run sentiment analysis:"
echo "  spark-submit \\"
echo "    --master local[*] \\"
echo "    --conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 \\"
echo "    --conf spark.driver.bindAddress=127.0.0.1 \\"
echo "    --conf spark.sql.shuffle.partitions=200 \\"
echo "    pipeline/run_sentiment.py"
echo ""

echo "Run ALS training:"
echo "  spark-submit \\"
echo "    --master local[*] \\"
echo "    --conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 \\"
echo "    --conf spark.driver.bindAddress=127.0.0.1 \\"
echo "    --conf spark.sql.shuffle.partitions=200 \\"
echo "    pipeline/train_als.py"
echo ""

echo "Export dashboard data:"
echo "  spark-submit \\"
echo "    --master local[*] \\"
echo "    --conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 \\"
echo "    --conf spark.driver.bindAddress=127.0.0.1 \\"
echo "    --conf spark.sql.shuffle.partitions=200 \\"
echo "    pipeline/export_dashboard_data.py"
echo ""

# =============================================================================
# PYSPARK INTERACTIVE COMMANDS
# =============================================================================

echo "=== PySpark Interactive Commands ==="
echo "Create Spark session in Python:"
echo "  from pyspark.sql import SparkSession"
echo "  spark = SparkSession.builder \\"
echo "      .appName('GameSphere') \\"
echo "      .config('spark.hadoop.fs.defaultFS', 'hdfs://localhost:9000') \\"
echo "      .config('spark.driver.bindAddress', '127.0.0.1') \\"
echo "      .config('spark.sql.shuffle.partitions', '200') \\"
echo "      .getOrCreate()"
echo ""

echo "Read data from HDFS:"
echo "  df = spark.read.option('header', 'true').csv('hdfs:///project/raw/steam_reviews.csv')"
echo "  df = spark.read.parquet('hdfs:///project/processed/steam_review_english.parquet')"
echo ""

echo "Basic DataFrame operations:"
echo "  df.show(10)           # Show first 10 rows"
echo "  df.count()            # Count rows"
echo "  df.columns            # Show column names"
echo "  df.dtypes             # Show data types"
echo "  df.describe().show()  # Summary statistics"
echo ""

echo "Write data to HDFS:"
echo "  df.write.mode('overwrite').parquet('hdfs:///project/processed/output.parquet')"
echo "  df.write.mode('overwrite').csv('hdfs:///project/processed/output.csv')"
echo ""

# =============================================================================
# MLFLOW INTEGRATION
# =============================================================================

echo "=== MLflow Integration ==="
echo "Start MLflow tracking in Python:"
echo "  import mlflow"
echo "  mlflow.start_run(run_name='data_processing')"
echo "  mlflow.log_metric('rows_processed', df.count())"
echo "  mlflow.log_param('input_file', 'steam_reviews.csv')"
echo "  mlflow.end_run()"
echo ""

echo "Start MLflow UI:"
echo "  mlflow ui --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 5000"
echo ""

# =============================================================================
# GAMEOSPHERE PIPELINE COMMANDS
# =============================================================================

echo "=== GameSphere Pipeline Commands ==="
echo "Complete pipeline execution:"
echo "  # 1. Data Cleaning"
echo "  make run-clean"
echo ""
echo "  # 2. Sentiment Analysis"
echo "  make run-sentiment"
echo ""
echo "  # 3. ALS Training"
echo "  make run-als"
echo ""
echo "  # 4. Data Export"
echo "  make run-export"
echo ""

echo "Manual pipeline execution:"
echo "  source .venv/bin/activate"
echo "  export SPARK_HOME=~/Spark/spark-3.5.3"
echo "  export HADOOP_HOME=~/Hadoop/hadoop-3.4.1"
echo "  export JAVA_HOME=/opt/homebrew/opt/openjdk@11"
echo ""
echo "  # Run each step"
echo "  python pipeline/clean_reviews.py"
echo "  python pipeline/run_sentiment.py"
echo "  python pipeline/train_als.py"
echo "  python pipeline/export_dashboard_data.py"
echo ""

# =============================================================================
# MONITORING & DEBUGGING
# =============================================================================

echo "=== Monitoring & Debugging ==="
echo "Check Spark UI (during job execution):"
echo "  http://localhost:4040"
echo ""

echo "View Spark logs:"
echo "  ls \$SPARK_HOME/logs/"
echo ""

echo "Test Spark connectivity to HDFS:"
echo "  pyspark --conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000"
echo "  # In PySpark shell:"
echo "  spark.read.text('hdfs:///project/raw/steam_reviews.csv').count()"
echo ""

echo "Check available resources:"
echo "  # In PySpark shell:"
echo "  spark.sparkContext.defaultParallelism"
echo "  spark.conf.get('spark.sql.shuffle.partitions')"
echo ""

# =============================================================================
# PERFORMANCE TUNING
# =============================================================================

echo "=== Performance Tuning ==="
echo "Adjust memory settings:"
echo "  spark-submit \\"
echo "    --driver-memory 4g \\"
echo "    --executor-memory 2g \\"
echo "    --conf spark.sql.shuffle.partitions=400 \\"
echo "    pipeline/train_als.py"
echo ""

echo "Cache frequently used DataFrames:"
echo "  df.cache()"
echo "  df.persist(StorageLevel.MEMORY_AND_DISK)"
echo ""

echo "Optimize file formats:"
echo "  # Use Parquet for better performance"
echo "  df.write.mode('overwrite').parquet('hdfs:///project/processed/data.parquet')"
echo ""

# =============================================================================
# QUICK TESTING COMMANDS
# =============================================================================

echo "=== Quick Testing Commands ==="
echo "Test PySpark installation:"
echo "  python -c \"from pyspark.sql import SparkSession; print('PySpark OK')\""
echo ""

echo "Test HDFS connectivity:"
echo "  python -c \\"
echo "    \"from pyspark.sql import SparkSession; \\"
echo "     spark = SparkSession.builder.config('spark.hadoop.fs.defaultFS', 'hdfs://localhost:9000').getOrCreate(); \\"
echo "     print('HDFS connectivity:', spark.read.text('hdfs:///').count() >= 0)\""
echo ""

echo "Test data loading:"
echo "  python -c \\"
echo "    \"from pyspark.sql import SparkSession; \\"
echo "     spark = SparkSession.builder.config('spark.hadoop.fs.defaultFS', 'hdfs://localhost:9000').getOrCreate(); \\"
echo "     df = spark.read.option('header', 'true').csv('hdfs:///project/raw/steam_reviews.csv'); \\"
echo "     print('Rows loaded:', df.count())\""
echo ""

echo ""
echo "=== PySpark Commands Reference Complete ==="
echo "Use these commands to interact with Spark and process GameSphere data"
