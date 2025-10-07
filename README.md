# 🎮 GameSphere Steam Game Recommender

A complete machine learning pipeline for Steam game recommendations using Apache Spark, collaborative filtering (ALS), BERT-based sentiment analysis, and modern web interfaces.

## 🚀 Quick Start

### One-Command Setup
```bash
make setup
```

This will:
- Install all dependencies (Java 11, Python 3.10, Hadoop, Spark)
- Configure HDFS with proper directory structure
- Set up Python virtual environment with all required packages
- Start HDFS services

### Data Pipeline

1. **Put raw data into HDFS:**
```bash
# Download steam_reviews.csv from Google Drive first
make put-raw RAW=/path/to/steam_reviews.csv
```

2. **Run the complete ML pipeline:**
```bash
make run-clean run-sentiment run-als run-export
```

### Launch Services

- **Streamlit Dashboard:** `make streamlit` → http://localhost:8501
- **Airflow Orchestration:** `make airflow-up` → http://localhost:8080
- **MLflow Tracking:** `make mlflow-ui` → http://localhost:5000
- **FastAPI Service:** `cd serving/fastapi && uvicorn main:app --reload` → http://localhost:8000

## 📊 Architecture

```
Raw Data (CSV) → HDFS → Spark Processing → ML Models → Dashboard/API
     ↓              ↓           ↓             ↓           ↓
Steam Reviews → Data Cleaning → Sentiment → ALS → Streamlit/FastAPI
                     ↓         Analysis   Model      ↓
                English Only      ↓         ↓    Recommendations
                     ↓         BERT NLP     ↓         ↓
                 Parquet       Scoring   User Recs  Visualizations
```

## 🛠 Technology Stack

- **Big Data:** Apache Spark 3.5.3, Hadoop 3.4.1, HDFS
- **Machine Learning:** Spark MLlib (ALS), Transformers (BERT), MLflow
- **Orchestration:** Apache Airflow 2.9.2 (Docker)
- **Frontend:** Streamlit, Plotly
- **API:** FastAPI, Uvicorn
- **Infrastructure:** Docker, Python 3.10, Java 11

## 📁 Project Structure

```
GameSphere_Steam_Game_Recommender/
├── AIRFLOW-PROJECT/           # Airflow orchestration
│   ├── dags/flow_dag.py      # Main pipeline DAG
│   ├── docker-compose.yaml   # Airflow services
│   └── requirements.txt      # Airflow dependencies
├── dashboards/
│   └── GameSphere.py         # Streamlit dashboard
├── pipeline/                 # Spark ML pipeline
│   ├── clean_reviews.py      # Data cleaning
│   ├── run_sentiment.py      # BERT sentiment analysis
│   ├── train_als.py          # ALS collaborative filtering
│   └── export_dashboard_data.py # Final data export
├── scripts/
│   ├── bootstrap_macos.sh    # Complete setup script
│   └── run_mlflow.sh         # MLflow UI launcher
├── serving/fastapi/          # REST API service
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # API dependencies
├── Makefile                 # All automation commands
└── requirements.txt         # Main Python dependencies
```

## 🔧 Manual Setup (Alternative)

If you prefer manual setup or the bootstrap script fails:

### 1. Install Dependencies
```bash
# macOS with Homebrew
brew install openjdk@11 python@3.10 wget git

# Set up directories
mkdir -p ~/Hadoop ~/Spark
```

### 2. Download & Install Hadoop/Spark
```bash
# Hadoop 3.4.1
cd ~/Hadoop
wget https://archive.apache.org/dist/hadoop/common/hadoop-3.4.1/hadoop-3.4.1.tar.gz
tar -xzf hadoop-3.4.1.tar.gz

# Spark 3.5.3
cd ~/Spark  
wget https://archive.apache.org/dist/spark/spark-3.5.3/spark-3.5.3-bin-hadoop3.tgz
tar -xzf spark-3.5.3-bin-hadoop3.tgz
mv spark-3.5.3-bin-hadoop3 spark-3.5.3
```

### 3. Environment Variables
Add to `~/.zshrc`:
```bash
# GameSphere env
export JAVA_HOME=/opt/homebrew/opt/openjdk@11
export PATH="$JAVA_HOME/bin:$PATH"
export HADOOP_HOME=~/Hadoop/hadoop-3.4.1
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export SPARK_HOME=~/Spark/spark-3.5.3
export PYSPARK_PYTHON=python3
export PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH
```

### 4. Python Environment
```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 📊 HDFS Data Layout

```
/project/
├── raw/                                    # Raw CSV files
│   └── steam_reviews.csv
├── processed/                              # Cleaned data
│   └── steam_review_english.parquet
├── data/processed/                         # Intermediate results
│   └── steam_sentiment_summary.parquet
└── outputs/                               # Final outputs
    ├── als_model/                         # Trained ALS model
    ├── user_recommendations.parquet       # Per-user recommendations
    ├── final_recommendations.parquet      # Final recommendation dataset
    └── app_recommendations.parquet        # App-level aggregations
```

## 🎯 Pipeline Steps

### 1. Data Cleaning (`clean_reviews.py`)
- Filters null values and invalid records
- Standardizes text formatting
- Extracts English-only reviews
- **Output:** `steam_review_english.parquet`

### 2. Sentiment Analysis (`run_sentiment.py`)
- BERT-based sentiment scoring using Transformers
- Aggregates sentiment by game (app_id)
- Tracks metrics in MLflow
- **Output:** `steam_sentiment_summary.parquet`

### 3. ALS Training (`train_als.py`)
- Collaborative filtering using Spark MLlib ALS
- Implicit feedback from user reviews
- Generates user-item recommendations
- **Output:** `als_model/`, `user_recommendations.parquet`

### 4. Data Export (`export_dashboard_data.py`)
- Combines sentiment and recommendation data
- Creates final datasets for dashboard consumption
- **Output:** `app_recommendations.parquet`, `final_recommendations.parquet`

## 🌐 Web Interfaces

### Streamlit Dashboard (Port 8501)
- Interactive game recommendations explorer
- Sentiment analysis visualizations
- Filtering and sorting capabilities
- Data export functionality

### FastAPI Service (Port 8000)
- RESTful API for recommendations
- Endpoints:
  - `GET /recommendations/{author_index}` - User recommendations
  - `GET /sentiment-leaderboard` - Top games by sentiment
  - `GET /games/{app_id}` - Game details
  - `GET /stats` - Overall statistics

### Airflow UI (Port 8080)
- Pipeline orchestration and monitoring
- DAG visualization and execution
- Task logs and debugging
- **Default login:** admin/admin

### MLflow UI (Port 5000)
- Experiment tracking and model versioning
- Metrics visualization
- Model artifact management

## 🐳 Docker Services

Airflow runs in Docker with the following services:
- **Webserver:** Airflow UI and API
- **Scheduler:** Task scheduling and execution
- **Worker:** Task execution (Celery)
- **PostgreSQL:** Metadata database
- **Redis:** Message broker

## 📈 Monitoring & Debugging

### HDFS Web UI
- **URL:** http://localhost:9870
- Monitor HDFS health, storage, and file system

### Spark UI
- Available during job execution
- Monitor stages, tasks, and performance

### Logs
- Airflow logs: `AIRFLOW-PROJECT/logs/`
- Spark logs: `$SPARK_HOME/logs/`
- Application logs: Console output

## 🔍 Troubleshooting

### Common Issues

1. **HDFS not starting:**
```bash
# Check if namenode is formatted
ls ~/Hadoop/hdfs-data/namenode/current
# If empty, format namenode
$HADOOP_HOME/bin/hdfs namenode -format
```

2. **Spark jobs failing:**
```bash
# Check HDFS connectivity
hdfs dfs -ls /project/
# Verify Spark configuration
$SPARK_HOME/bin/spark-shell --conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000
```

3. **Python dependencies:**
```bash
# Reinstall requirements
source .venv/bin/activate
pip install --upgrade -r requirements.txt
```

4. **Airflow connection issues:**
```bash
# Restart Airflow services
make airflow-down
make airflow-up
```

### Performance Tuning

- Adjust `spark.sql.shuffle.partitions` based on data size
- Increase Spark driver/executor memory for large datasets
- Tune ALS parameters (rank, iterations, regularization)
- Use appropriate HDFS replication factor

## 📝 Development

### Adding New Pipeline Steps
1. Create new Python script in `pipeline/`
2. Add Spark session with HDFS configuration
3. Update `Makefile` with new target
4. Add task to Airflow DAG

### Extending the API
1. Add new endpoints to `serving/fastapi/main.py`
2. Update data models in Pydantic schemas
3. Test with FastAPI automatic docs at `/docs`

### Dashboard Enhancements
1. Modify `dashboards/GameSphere.py`
2. Add new Plotly visualizations
3. Extend filtering and interaction capabilities

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and test locally
4. Commit changes: `git commit -am 'Add new feature'`
5. Push to branch: `git push origin feature/new-feature`
6. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Apache Spark and Hadoop communities
- Hugging Face Transformers library
- Streamlit and FastAPI frameworks
- Steam for providing review data access
