# GameSphere Steam Recommender - Makefile
# One-command setup and execution for the complete pipeline

.PHONY: setup hdfs-start hdfs-stop put-raw run-clean run-sentiment run-als run-export mlflow-ui airflow-up airflow-down streamlit help

# Default target
help:
	@echo "GameSphere Steam Recommender - Available Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup          - Run complete macOS bootstrap setup"
	@echo ""
	@echo "HDFS Management:"
	@echo "  make hdfs-start     - Start HDFS services"
	@echo "  make hdfs-stop      - Stop HDFS services"
	@echo ""
	@echo "Data Management:"
	@echo "  make put-raw RAW=<path>  - Upload raw CSV to HDFS"
	@echo ""
	@echo "Pipeline Execution:"
	@echo "  make run-clean      - Run data cleaning step"
	@echo "  make run-sentiment  - Run sentiment analysis step"
	@echo "  make run-als        - Run ALS recommendation training"
	@echo "  make run-export     - Export final dashboard data"
	@echo ""
	@echo "Services:"
	@echo "  make mlflow-ui      - Start MLflow tracking UI"
	@echo "  make airflow-up     - Start Airflow with Docker"
	@echo "  make airflow-down   - Stop Airflow services"
	@echo "  make streamlit      - Start Streamlit dashboard"
	@echo ""
	@echo "Example workflow:"
	@echo "  make setup"
	@echo "  make put-raw RAW=/path/to/steam_reviews.csv"
	@echo "  make run-clean run-sentiment run-als run-export"
	@echo "  make streamlit"

# Setup - Run bootstrap script
setup:
	@echo "🚀 Running GameSphere macOS bootstrap..."
	./scripts/bootstrap_macos.sh

# HDFS Management
hdfs-start:
	@echo "🔧 Starting HDFS services..."
	${HADOOP_HOME}/sbin/start-dfs.sh

hdfs-stop:
	@echo "🔧 Stopping HDFS services..."
	${HADOOP_HOME}/sbin/stop-dfs.sh

# Data Upload
put-raw:
	@if [ -z "$(RAW)" ]; then \
		echo "❌ Error: Please specify RAW path. Usage: make put-raw RAW=/path/to/steam_reviews.csv"; \
		exit 1; \
	fi
	@echo "📤 Uploading $(RAW) to HDFS..."
	hdfs dfs -put $(RAW) /project/raw/

# Pipeline Steps
run-clean:
	@echo "🧹 Running data cleaning pipeline..."
	${SPARK_HOME}/bin/spark-submit \
		--master local[*] \
		--conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 \
		--conf spark.driver.bindAddress=127.0.0.1 \
		--conf spark.sql.shuffle.partitions=200 \
		pipeline/clean_reviews.py

run-sentiment:
	@echo "🎭 Running sentiment analysis pipeline..."
	${SPARK_HOME}/bin/spark-submit \
		--master local[*] \
		--conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 \
		--conf spark.driver.bindAddress=127.0.0.1 \
		--conf spark.sql.shuffle.partitions=200 \
		pipeline/run_sentiment.py

run-als:
	@echo "🤖 Running ALS recommendation training..."
	${SPARK_HOME}/bin/spark-submit \
		--master local[*] \
		--conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 \
		--conf spark.driver.bindAddress=127.0.0.1 \
		--conf spark.sql.shuffle.partitions=200 \
		pipeline/train_als.py

run-export:
	@echo "📊 Exporting dashboard data..."
	${SPARK_HOME}/bin/spark-submit \
		--master local[*] \
		--conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 \
		--conf spark.driver.bindAddress=127.0.0.1 \
		--conf spark.sql.shuffle.partitions=200 \
		pipeline/export_dashboard_data.py

# MLflow
mlflow-ui:
	@echo "📈 Starting MLflow UI..."
	@echo "MLflow will be available at: http://localhost:5000"
	mlflow ui --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns --host 0.0.0.0 --port 5000

# Airflow
airflow-up:
	@echo "🌬️  Starting Airflow services..."
	@echo "Airflow UI will be available at: http://localhost:8080"
	cd AIRFLOW-PROJECT && docker compose up -d

airflow-down:
	@echo "🌬️  Stopping Airflow services..."
	cd AIRFLOW-PROJECT && docker compose down

# Streamlit Dashboard
streamlit:
	@echo "📊 Starting Streamlit dashboard..."
	@echo "Dashboard will be available at: http://localhost:8501"
	streamlit run dashboards/GameSphere.py

# Development helpers
clean-logs:
	@echo "🧹 Cleaning up log files..."
	find . -name "*.log" -delete
	find . -name "spark-warehouse" -type d -exec rm -rf {} + 2>/dev/null || true

status:
	@echo "📊 GameSphere Status Check:"
	@echo ""
	@echo "HDFS Status:"
	@hdfs dfsadmin -report 2>/dev/null || echo "  ❌ HDFS not running"
	@echo ""
	@echo "Python Environment:"
	@if [ -d ".venv" ]; then echo "  ✅ Virtual environment exists"; else echo "  ❌ Virtual environment missing"; fi
	@echo ""
	@echo "Required Directories:"
	@for dir in scripts pipeline dashboards serving AIRFLOW-PROJECT; do \
		if [ -d "$$dir" ]; then echo "  ✅ $$dir/"; else echo "  ❌ $$dir/ missing"; fi; \
	done
