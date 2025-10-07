"""
GameSphere Steam Recommender - Airflow DAG
Orchestrates the complete ML pipeline from data cleaning to final export
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

# Add pipeline directory to Python path
sys.path.append('/opt/airflow/dags/pipeline')

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
    'gamesphere_flow',
    default_args=default_args,
    description='GameSphere Steam Recommender ML Pipeline',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    tags=['gamesphere', 'ml', 'spark', 'recommendations'],
)

# Python functions for each pipeline stage
def run_clean_reviews():
    """Execute data cleaning pipeline"""
    import clean_reviews
    clean_reviews.main()

def run_sentiment_analysis():
    """Execute sentiment analysis pipeline"""
    import run_sentiment
    run_sentiment.main()

def run_als_training():
    """Execute ALS model training pipeline"""
    import train_als
    train_als.main()

def run_export_data():
    """Execute data export pipeline"""
    import export_dashboard_data
    export_dashboard_data.main()

# Task 1: Clean Reviews
clean_task = PythonOperator(
    task_id='clean_reviews',
    python_callable=run_clean_reviews,
    dag=dag,
)

# Task 2: Sentiment Analysis
sentiment_task = PythonOperator(
    task_id='sentiment_analysis',
    python_callable=run_sentiment_analysis,
    dag=dag,
)

# Task 3: ALS Training
als_task = PythonOperator(
    task_id='train_als_model',
    python_callable=run_als_training,
    dag=dag,
)

# Task 4: Export Dashboard Data
export_task = PythonOperator(
    task_id='export_dashboard_data',
    python_callable=run_export_data,
    dag=dag,
)

# Define task dependencies
clean_task >> sentiment_task >> als_task >> export_task
