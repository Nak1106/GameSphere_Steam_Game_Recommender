"""
GameSphere Steam Recommender - Hybrid Airflow DAG
Orchestrates the ML pipeline by executing local PySpark scripts that can access HDFS
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Default arguments for the DAG
default_args = {
    'owner': 'gamesphere',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG
dag = DAG(
    'gamesphere_flow_hybrid',
    default_args=default_args,
    description='GameSphere Steam Recommender ML Pipeline (Hybrid)',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    tags=['gamesphere', 'ml', 'spark', 'recommendations', 'hybrid'],
)

# Base command to set up environment and run Python scripts
base_cmd = """
cd /Users/spartan/GameSphere_Steam_Game_Recommender && \
export JAVA_HOME=/opt/homebrew/opt/openjdk@11 && \
export HADOOP_HOME=/Users/spartan/Hadoop/hadoop-3.4.1 && \
export SPARK_HOME=/Users/spartan/Spark/spark-3.5.3/spark-3.5.3-bin-hadoop3 && \
source .venv/bin/activate && \
"""

# Task 1: Clean Reviews
clean_task = BashOperator(
    task_id='clean_reviews',
    bash_command=base_cmd + 'python pipeline/clean_reviews.py',
    dag=dag,
)

# Task 2: Sentiment Analysis
sentiment_task = BashOperator(
    task_id='sentiment_analysis', 
    bash_command=base_cmd + 'python pipeline/run_sentiment.py',
    dag=dag,
)

# Task 3: ALS Training
als_task = BashOperator(
    task_id='train_als_model',
    bash_command=base_cmd + 'python pipeline/train_als.py',
    dag=dag,
)

# Task 4: Export Dashboard Data
export_task = BashOperator(
    task_id='export_dashboard_data',
    bash_command=base_cmd + 'python pipeline/export_dashboard_data.py',
    dag=dag,
)

# Define task dependencies
clean_task >> sentiment_task >> als_task >> export_task
