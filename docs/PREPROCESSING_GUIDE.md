# 🎮 GameSphere Steam Reviews Preprocessing Guide

## 📊 **Dataset Overview**

### **Raw Data Statistics**
- **Total Records:** 48,296,896 Steam reviews
- **File Size:** 7.6 GB (CSV format)
- **Source:** Steam Review Dataset
- **Storage:** HDFS cluster (`/project/raw/steam_reviews.csv`)

### **Data Schema Analysis**
```
Column Name                    | Type    | Description
-------------------------------|---------|------------------------------------------
app_id                        | Integer | Unique Steam game identifier
app_name                      | String  | Game title/name
review_id                     | Integer | Unique review identifier
language                      | String  | Review language (english, schinese, etc.)
review                        | Text    | User review content (main target)
timestamp_created             | Unix    | Review creation timestamp
timestamp_updated             | Unix    | Last review update timestamp
recommended                   | Boolean | User recommendation (True/False)
votes_helpful                 | Integer | Helpful votes count
votes_funny                   | Integer | Funny votes count
weighted_vote_score           | Float   | Steam's weighted vote algorithm score
comment_count                 | Integer | Number of comments on review
steam_purchase                | Boolean | Purchased through Steam
received_for_free             | Boolean | Received game for free
written_during_early_access   | Boolean | Written during early access
author.steamid                | String  | Author's Steam ID
author.num_games_owned        | Integer | Author's total games owned
author.num_reviews            | Integer | Author's total reviews written
author.playtime_forever       | Float   | Total playtime (minutes)
author.playtime_last_two_weeks| Float   | Recent playtime (minutes)
author.playtime_at_review     | Float   | Playtime when review written
author.last_played            | Unix    | Last played timestamp
```

---

## 🔄 **Preprocessing Pipeline Overview**

The GameSphere preprocessing pipeline consists of **4 sequential stages**, each designed to transform raw Steam reviews into ML-ready datasets:

```
Raw Steam Reviews (48M records)
         ↓
    [STAGE 1: Data Cleaning]
         ↓
    English Reviews Only (~30M records)
         ↓
    [STAGE 2: Sentiment Analysis]
         ↓
    Sentiment-Labeled Reviews
         ↓
    [STAGE 3: ALS Model Training]
         ↓
    User-Item Recommendations
         ↓
    [STAGE 4: Data Export & Aggregation]
         ↓
    Dashboard-Ready Datasets
```

---

## 📋 **Stage 1: Data Cleaning & Filtering**

### **Objective**
Transform raw Steam reviews into a clean, English-only dataset suitable for NLP processing.

### **Input**
- **Source:** `hdfs:///project/raw/steam_reviews.csv`
- **Records:** 48,296,896 reviews
- **Languages:** Multiple (english, schinese, spanish, french, etc.)

### **Processing Steps**

#### **1.1 Data Quality Validation**
```python
# Remove records with critical null values
cleaned_df = raw_df.filter(
    col("review").isNotNull() & 
    col("app_id").isNotNull() & 
    col("author.steamid").isNotNull()
)
```

#### **1.2 Language Filtering**
```python
# Filter for English reviews only
english_df = cleaned_df.filter(col("language") == "english")
```

#### **1.3 Text Preprocessing**
```python
# Clean and standardize review text
cleaned_df = cleaned_df.withColumn(
    "review_clean", 
    regexp_replace(trim(lower(col("review"))), r"[^\w\s]", " ")
)
```

#### **1.4 Data Type Standardization**
- Convert timestamps to proper datetime format
- Ensure boolean fields are properly typed
- Handle numeric field inconsistencies

### **Output**
- **Destination:** `hdfs:///project/processed/steam_review_english.parquet`
- **Expected Records:** ~30M English reviews (62% of original)
- **Format:** Parquet (optimized for Spark processing)

### **Quality Metrics**
- **Null Value Removal:** < 1% data loss
- **Language Filtering:** ~38% reduction (multilingual → English only)
- **Text Cleaning:** 100% reviews processed
- **Data Integrity:** All critical fields validated

---

## 🎭 **Stage 2: Sentiment Analysis**

### **Objective**
Apply BERT-based sentiment analysis to English reviews and aggregate sentiment scores by game.

### **Input**
- **Source:** `hdfs:///project/processed/steam_review_english.parquet`
- **Records:** ~30M English reviews

### **Processing Steps**

#### **2.1 BERT Model Initialization**
```python
from transformers import pipeline
sentiment_pipeline = pipeline(
    "sentiment-analysis", 
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    return_all_scores=True
)
```

#### **2.2 Batch Sentiment Processing**
```python
# Process reviews in batches for efficiency
def analyze_sentiment_batch(reviews):
    results = []
    for review in reviews:
        if review and len(review.strip()) > 0:
            scores = sentiment_pipeline(review[:512])  # Truncate to 512 chars
            pos_score = next((s['score'] for s in scores[0] if s['label'] == 'POSITIVE'), 0.5)
            results.append(float(pos_score))
    return results
```

#### **2.3 Sentiment Score Assignment**
- **Range:** 0.0 (negative) to 1.0 (positive)
- **Neutral Default:** 0.5 for processing errors
- **Text Limit:** 512 characters (BERT constraint)

#### **2.4 Game-Level Aggregation**
```python
sentiment_summary = sentiment_df.groupBy("app_id") \
    .agg(
        avg("sentiment_score").alias("avg_sentiment"),
        count("*").alias("review_count"),
        avg(when(col("sentiment_score") > 0.6, 1).otherwise(0)).alias("positive_ratio")
    )
```

### **Output**
- **Destination:** `hdfs:///project/data/processed/steam_sentiment_summary.parquet`
- **Records:** ~50K unique games with sentiment metrics
- **Metrics:** Average sentiment, positive ratio, review count per game

### **MLflow Tracking**
- **Experiment:** `sentiment_analysis`
- **Metrics Logged:**
  - Total reviews processed
  - Average sentiment score
  - Processing time
  - Model performance metrics

---

## 🤖 **Stage 3: ALS Collaborative Filtering**

### **Objective**
Train an ALS (Alternating Least Squares) model for collaborative filtering recommendations.

### **Input**
- **Source:** `hdfs:///project/processed/steam_review_english.parquet`
- **Features:** User-item interactions (implicit feedback)

### **Processing Steps**

#### **3.1 Rating Matrix Construction**
```python
# Create implicit ratings from reviews
ratings_df = reviews_df.select("author.steamid", "app_id") \
    .withColumn("rating", lit(1.0))  # Implicit positive rating

# Index string columns for ALS
author_indexer = StringIndexer(inputCol="author.steamid", outputCol="user")
app_indexer = StringIndexer(inputCol="app_id", outputCol="item")
```

#### **3.2 ALS Model Configuration**
```python
als = ALS(
    rank=10,                    # Latent factors
    maxIter=10,                 # Training iterations
    regParam=0.1,               # Regularization
    userCol="user",
    itemCol="item", 
    ratingCol="rating",
    coldStartStrategy="drop",   # Handle new users/items
    implicitPrefs=True          # Implicit feedback mode
)
```

#### **3.3 Model Training & Evaluation**
- **Train/Test Split:** 80/20
- **Evaluation Metric:** RMSE (Root Mean Square Error)
- **Cross-Validation:** K-fold validation for hyperparameter tuning

#### **3.4 Recommendation Generation**
```python
# Generate top-10 recommendations for all users
user_recs = model.recommendForAllUsers(10)
```

### **Output**
- **Model:** `hdfs:///project/outputs/als_model/`
- **Recommendations:** `hdfs:///project/outputs/user_recommendations.parquet`
- **Records:** ~2M users with 10 recommendations each

### **MLflow Tracking**
- **Experiment:** `als_training`
- **Artifacts:** Trained model, feature mappings
- **Metrics:** RMSE, training time, model parameters

---

## 📊 **Stage 4: Data Export & Dashboard Preparation**

### **Objective**
Combine all processed data into dashboard-ready formats with comprehensive metrics.

### **Input Sources**
- Sentiment summary data
- ALS recommendations
- Original review metadata

### **Processing Steps**

#### **4.1 Data Integration**
```python
# Combine sentiment and recommendation data
final_dataset = sentiment_summary.join(
    app_metadata, 
    sentiment_summary.app_id == app_metadata.app_id,
    "inner"
)
```

#### **4.2 Metric Calculation**
- **Game Popularity:** Review count, user engagement
- **Sentiment Metrics:** Average sentiment, positive ratio
- **Recommendation Strength:** ALS confidence scores
- **Temporal Analysis:** Review trends over time

#### **4.3 Multi-Format Export**
```python
# Export to multiple formats for different use cases
app_recommendations.write.mode("overwrite") \
    .parquet("hdfs:///project/outputs/app_recommendations.parquet")

# Copy to local storage for dashboard access
app_recommendations.coalesce(1).write.mode("overwrite") \
    .option("header", "true") \
    .csv("data/cleaned_data/final_recommendations.csv")
```

### **Output**
- **Primary:** `hdfs:///project/outputs/app_recommendations.parquet`
- **Dashboard Copy:** `data/cleaned_data/final_recommendations.csv`
- **User Recs:** `hdfs:///project/outputs/final_recommendations.parquet`

---

## 🔍 **Data Quality Assurance**

### **Validation Checkpoints**

#### **Stage 1 Validation**
- [ ] **Record Count:** English reviews ≥ 25M (expected ~30M)
- [ ] **Null Values:** < 0.1% in critical fields
- [ ] **Language Purity:** 100% English language reviews
- [ ] **Text Quality:** All reviews have clean, processable text

#### **Stage 2 Validation**
- [ ] **Sentiment Range:** All scores between 0.0-1.0
- [ ] **Processing Coverage:** 100% reviews processed
- [ ] **Aggregation Accuracy:** Game-level metrics computed correctly
- [ ] **Performance:** < 2 hours processing time

#### **Stage 3 Validation**
- [ ] **Model Convergence:** RMSE improvement over iterations
- [ ] **Recommendation Quality:** Diverse, relevant suggestions
- [ ] **Coverage:** Recommendations for ≥ 90% of active users
- [ ] **Cold Start:** Proper handling of new users/items

#### **Stage 4 Validation**
- [ ] **Data Integrity:** All joins successful, no data loss
- [ ] **Metric Accuracy:** Calculated values within expected ranges
- [ ] **Export Success:** All output files created successfully
- [ ] **Dashboard Compatibility:** Data loads correctly in Streamlit

---

## 🚀 **Execution Commands**

### **Manual Execution (Recommended for Testing)**
```bash
# Stage 1: Data Cleaning
make run-clean

# Stage 2: Sentiment Analysis  
make run-sentiment

# Stage 3: ALS Training
make run-als

# Stage 4: Data Export
make run-export
```

### **Airflow Orchestration (Production)**
```bash
# Start Airflow UI
make airflow-up

# Navigate to: http://localhost:8080
# Login: admin / admin
# Trigger: gamesphere_flow DAG
```

### **Monitoring & Debugging**
```bash
# Check HDFS data
hdfs dfs -ls /project/processed/
hdfs dfs -du -h /project/outputs/

# Monitor Spark jobs
# Spark UI: http://localhost:4040 (during execution)

# MLflow tracking
./scripts/run_mlflow.sh
# MLflow UI: http://localhost:5000
```

---

## 📈 **Expected Performance Metrics**

### **Processing Times (Estimated)**
- **Stage 1 (Cleaning):** 15-20 minutes
- **Stage 2 (Sentiment):** 2-3 hours (BERT processing)
- **Stage 3 (ALS):** 30-45 minutes
- **Stage 4 (Export):** 10-15 minutes
- **Total Pipeline:** ~3.5 hours

### **Resource Requirements**
- **Memory:** 8GB+ recommended
- **CPU:** 4+ cores for parallel processing
- **Storage:** 50GB+ for intermediate files
- **Network:** Stable connection for model downloads

### **Output Data Sizes**
- **English Reviews:** ~4GB (Parquet)
- **Sentiment Summary:** ~50MB
- **ALS Model:** ~200MB
- **Final Recommendations:** ~500MB

---

## 🎯 **Success Criteria**

### **Data Quality**
- ✅ **Completeness:** All stages produce expected outputs
- ✅ **Accuracy:** Sentiment scores align with manual validation
- ✅ **Consistency:** No data corruption or format issues
- ✅ **Performance:** Processing completes within time limits

### **Business Value**
- ✅ **Recommendation Quality:** Diverse, relevant game suggestions
- ✅ **Sentiment Insights:** Accurate game sentiment analysis
- ✅ **User Coverage:** Recommendations for majority of users
- ✅ **Dashboard Ready:** Data integrates seamlessly with UI

---

## 📝 **Troubleshooting Guide**

### **Common Issues & Solutions**

#### **Memory Errors**
```bash
# Increase Spark driver memory
spark-submit --driver-memory 8g --executor-memory 4g pipeline/clean_reviews.py
```

#### **HDFS Connection Issues**
```bash
# Verify HDFS is running
jps | grep -E "(NameNode|DataNode)"

# Check HDFS health
hdfs dfsadmin -report
```

#### **Sentiment Analysis Timeouts**
```bash
# Reduce batch size in run_sentiment.py
# Process in smaller chunks for stability
```

#### **ALS Training Failures**
```bash
# Check data sparsity and adjust ALS parameters
# Increase regularization if overfitting
```

---

## 🏆 **Article Highlights**

### **Technical Innovation**
- **Scale:** Processing 48M+ Steam reviews with Apache Spark
- **AI Integration:** BERT-based sentiment analysis at scale
- **Real-time:** End-to-end pipeline from raw data to recommendations
- **Architecture:** Modern data stack (Spark + HDFS + MLflow + Airflow)

### **Business Impact**
- **Personalization:** Individual game recommendations for millions of users
- **Insights:** Game sentiment analysis for developers and players
- **Scalability:** Architecture handles growing datasets efficiently
- **Automation:** Fully orchestrated pipeline with monitoring

### **Key Metrics for Article**
- **48.3M reviews processed**
- **30M+ English reviews analyzed**
- **50K+ games with sentiment scores**
- **2M+ users with personalized recommendations**
- **3.5 hour end-to-end processing time**

---

*This preprocessing pipeline forms the foundation of GameSphere's recommendation engine, transforming raw Steam review data into actionable insights and personalized recommendations.*
