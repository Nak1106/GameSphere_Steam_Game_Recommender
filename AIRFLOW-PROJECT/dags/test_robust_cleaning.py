"""
Test DAG for robust data cleaning pipeline
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
    'test_robust_cleaning',
    default_args=default_args,
    description='Test robust data cleaning with detailed logging',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    tags=['test', 'cleaning', 'robust'],
)

# Common environment variables
common_env = {
    'JAVA_HOME': '/usr/lib/jvm/java-17-openjdk-arm64',
    'SPARK_HOME': '/opt/spark',
    'HADOOP_HOME': '/opt/hadoop',
    'HADOOP_CONF_DIR': '/opt/hadoop/etc/hadoop',
}

# Test robust cleaning
test_task = BashOperator(
    task_id='test_robust_cleaning',
    bash_command='/opt/spark/bin/spark-submit --master local[2] --conf spark.hadoop.fs.defaultFS=hdfs://host.docker.internal:9000 --conf spark.driver.bindAddress=0.0.0.0 --conf spark.sql.adaptive.enabled=false /opt/airflow/dags/pipeline/clean_reviews_robust.py',
    env=common_env,
    dag=dag,
)
