"""
GameSphere Steam Recommender - Docker-Compatible Airflow DAG
Uses proper container paths and spark-submit with HDFS networking
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
    'gamesphere_flow_docker',
    default_args=default_args,
    description='GameSphere Steam Recommender ML Pipeline (Docker)',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    tags=['gamesphere', 'ml', 'spark', 'recommendations', 'docker'],
)

# Common environment variables for all tasks
common_env = {
    'JAVA_HOME': '/usr/lib/jvm/java-17-openjdk-arm64',
    'SPARK_HOME': '/opt/spark',
    'HADOOP_HOME': '/opt/hadoop',
    'HADOOP_CONF_DIR': '/opt/hadoop/etc/hadoop',
}

# Base spark-submit command with proper HDFS configuration
spark_submit_base = "/opt/spark/bin/spark-submit --master local[*] --conf spark.hadoop.fs.defaultFS=hdfs://host.docker.internal:9000 --conf spark.driver.bindAddress=0.0.0.0 --conf spark.sql.shuffle.partitions=200 --conf spark.serializer=org.apache.spark.serializer.KryoSerializer"

# Task 1: Clean Reviews
clean_task = BashOperator(
    task_id='clean_reviews',
    bash_command=f'{spark_submit_base} /opt/airflow/dags/pipeline/clean_reviews_docker.py',
    env=common_env,
    dag=dag,
)

# Task 2: Sentiment Analysis
sentiment_task = BashOperator(
    task_id='sentiment_analysis', 
    bash_command=f'{spark_submit_base} /opt/airflow/dags/pipeline/run_sentiment.py',
    env=common_env,
    dag=dag,
)

# Task 3: ALS Training
als_task = BashOperator(
    task_id='train_als_model',
    bash_command=f'{spark_submit_base} /opt/airflow/dags/pipeline/train_als.py',
    env=common_env,
    dag=dag,
)

# Task 4: Export Dashboard Data
export_task = BashOperator(
    task_id='export_dashboard_data',
    bash_command=f'{spark_submit_base} /opt/airflow/dags/pipeline/export_dashboard_data.py',
    env=common_env,
    dag=dag,
)

# Define task dependencies
clean_task >> sentiment_task >> als_task >> export_task
