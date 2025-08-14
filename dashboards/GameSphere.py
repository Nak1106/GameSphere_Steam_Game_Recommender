import os
import streamlit as st
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, date_format
import plotly.express as px

# ✅ Spark Environment Setup for macOS
os.environ["JAVA_HOME"] = "/opt/homebrew/opt/openjdk@11"
os.environ["PATH"] = f"{os.environ['JAVA_HOME']}/bin:/opt/homebrew/bin:" + os.environ["PATH"]

# ✅ Start Spark Session
spark = SparkSession.builder \
    .appName("GameSphere Full App") \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .config("spark.driver.memory", "6g") \
    .config("spark.executor.memory", "6g") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# ✅ Load HDFS Data
recommendations_df = spark.read.parquet("hdfs:///project/outputs/app_recommendations.parquet")
games_df = spark.read.parquet("hdfs:///project/data/mappings/games_mapping.parquet")
author_mapping = spark.read.parquet("hdfs:///project/data/mappings/author_mapping.parquet")
df = spark.read.parquet("hdfs:///project/processed/steam_review_english.parquet")
sentiment_summary = spark.read.parquet("hdfs:///project/data/processed/steam_sentiment_summary.parquet")

# ✅ Explode ALS recommendations
exploded_recs = recommendations_df.withColumn("rec", explode("recommendations")) \
    .select(col("author_index"), col("rec.app_index").alias("app_index"), col("rec.rating").alias("predicted_rating"))

# ✅ Join with games and sentiment
full_recs = exploded_recs.join(games_df, on="app_index", how="inner")
full_recs_with_sentiment = full_recs.join(
    sentiment_summary,
    full_recs.app_name == sentiment_summary.app_name,
    "left"
).select(
    full_recs["author_index"],
    full_recs["app_name"],
    "predicted_rating",
    "avg_sentiment_score",
    "positive_reviews",
    "negative_reviews",
    "percent_positive",
    "percent_negative"
)

# ✅ Streamlit App Tabs
st.set_page_config(layout="wide")
tab1, tab2, tab3 = st.tabs(["🎮 Game Recommendations", "📊 Interactive Dashboard", "📊 EDA Insights"])

# ✅ Tab 1: Personalized Game Recommendations
with tab1:
    st.title("🎮 GameSphere - Game Recommendations")
    steam_id = st.text_input("Enter your Steam Author ID (author_steamid):")

    if st.button("Get Recommendations"):
        if steam_id.isdigit():
            steam_id_long = int(steam_id)
            match = author_mapping.filter(col("author_steamid") == steam_id_long).select("author_index").collect()
            if match:
                user_index = match[0]["author_index"]
                user_stats = df.filter(col("author_steamid") == steam_id_long)

                total_reviews = user_stats.count()
                avg_playtime = user_stats.agg({"author_playtime_forever": "sum"}).collect()[0][0] / 3600
                total_games = user_stats.select("app_id").distinct().count()

                kcol1, kcol2, kcol3 = st.columns(3)
                kcol1.metric("📝 Total Reviews", f"{total_reviews}")
                kcol2.metric("🎮 Games Reviewed", f"{total_games}")
                kcol3.metric("⏱️ Total Playtime", f"{avg_playtime:.1f} hrs")

                user_recs = full_recs_with_sentiment.filter(col("author_index") == user_index).toPandas()

                if not user_recs.empty:
                    sort_by = st.selectbox("Sort by", ["predicted_rating", "percent_positive"])
                    sorted_recs = user_recs.sort_values(by=sort_by, ascending=False)
                    st.dataframe(sorted_recs)
                else:
                    st.warning("No recommendations found.")
            else:
                st.error("Steam ID not found.")
        else:
            st.warning("Please enter a valid numeric Steam ID.")

# ✅ Tab 2: Sentiment Dashboard
with tab2:
    st.title("📊 Sentiment Leaderboard")
    top_sentiment = full_recs_with_sentiment.groupBy("app_name").agg({
        "percent_positive": "avg",
        "avg_sentiment_score": "avg",
        "predicted_rating": "avg"
    }).toPandas().sort_values(by="avg(percent_positive)", ascending=False).head(20)

    fig = px.bar(top_sentiment, x="avg(percent_positive)", y="app_name", orientation="h",
                 title="Top 20 Games by % Positive Sentiment")
    st.plotly_chart(fig, use_container_width=True)

# ✅ Tab 3: EDA on Raw Reviews
with tab3:
    st.title("📊 Exploratory Data Analysis (EDA)")
    top_games = df.groupBy("app_name").count().orderBy(col("count").desc()).limit(15).toPandas()
    fig1 = px.bar(top_games.sort_values("count"), x="count", y="app_name", orientation="h",
                  title="Top 15 Most Reviewed Games")
    st.plotly_chart(fig1, use_container_width=True)
