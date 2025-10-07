#!/usr/bin/env python3
"""
GameSphere Steam Recommender - Streamlit Dashboard
Interactive dashboard for exploring Steam game recommendations and sentiment analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="GameSphere - Steam Game Recommender",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_recommendations_data():
    """Load recommendations data from parquet files"""
    try:
        # Try to load from local parquet file first (copied from HDFS)
        local_path = "app_recommendations.parquet"
        if os.path.exists(local_path):
            logger.info("Loading recommendations from local parquet file")
            return pd.read_parquet(local_path)
        
        # Fallback: try to read from HDFS using Spark (if available)
        try:
            from pyspark.sql import SparkSession
            
            # Create Spark session (reuse global session)
            if 'spark' not in st.session_state:
                st.session_state.spark = SparkSession.builder \
                    .appName("GameSphere-Dashboard") \
                    .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
                    .config("spark.driver.bindAddress", "127.0.0.1") \
                    .config("spark.sql.shuffle.partitions", "50") \
                    .getOrCreate()
            
            spark = st.session_state.spark
            
            logger.info("Loading recommendations from HDFS")
            df_spark = spark.read.parquet("hdfs:///project/outputs/app_recommendations.parquet")
            return df_spark.toPandas()
            
        except Exception as e:
            logger.warning(f"Could not load from HDFS: {e}")
            
        # Final fallback: create sample data
        logger.info("Creating sample data for demonstration")
        return pd.DataFrame({
            'app_id': [f'game_{i}' for i in range(1, 21)],
            'avg_sentiment': [0.6 + (i * 0.02) for i in range(20)],
            'positive_ratio': [0.5 + (i * 0.025) for i in range(20)],
            'review_count': [100 + (i * 50) for i in range(20)],
            'total_reviews': [120 + (i * 60) for i in range(20)]
        })
        
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        st.error(f"Error loading recommendations data: {e}")
        return pd.DataFrame()

def create_sentiment_distribution_chart(df):
    """Create sentiment distribution histogram"""
    fig = px.histogram(
        df, 
        x='avg_sentiment',
        nbins=20,
        title='Distribution of Average Sentiment Scores',
        labels={'avg_sentiment': 'Average Sentiment Score', 'count': 'Number of Games'},
        color_discrete_sequence=['#1f77b4']
    )
    fig.update_layout(
        xaxis_title="Average Sentiment Score",
        yaxis_title="Number of Games",
        showlegend=False
    )
    return fig

def create_sentiment_vs_reviews_scatter(df):
    """Create scatter plot of sentiment vs review count"""
    fig = px.scatter(
        df,
        x='review_count',
        y='avg_sentiment',
        size='positive_ratio',
        hover_data=['app_id'],
        title='Sentiment Score vs Review Count',
        labels={
            'review_count': 'Number of Reviews',
            'avg_sentiment': 'Average Sentiment Score',
            'positive_ratio': 'Positive Review Ratio'
        },
        color='positive_ratio',
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(
        xaxis_title="Number of Reviews",
        yaxis_title="Average Sentiment Score"
    )
    return fig

def create_top_games_chart(df, metric='avg_sentiment', top_n=10):
    """Create bar chart of top games by specified metric"""
    top_games = df.nlargest(top_n, metric)
    
    fig = px.bar(
        top_games,
        x=metric,
        y='app_id',
        orientation='h',
        title=f'Top {top_n} Games by {metric.replace("_", " ").title()}',
        labels={metric: metric.replace("_", " ").title(), 'app_id': 'Game ID'},
        color=metric,
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=400
    )
    return fig

def main():
    """Main dashboard function"""
    # Header
    st.title("🎮 GameSphere - Steam Game Recommender")
    st.markdown("**Discover the best Steam games through AI-powered sentiment analysis and collaborative filtering**")
    
    # Load data
    with st.spinner("Loading recommendation data..."):
        df = load_recommendations_data()
    
    if df.empty:
        st.error("No data available. Please run the pipeline first.")
        st.info("Run: `make run-clean run-sentiment run-als run-export` to generate data")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Sentiment filter
    min_sentiment = st.sidebar.slider(
        "Minimum Sentiment Score",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1
    )
    
    # Review count filter
    min_reviews = st.sidebar.slider(
        "Minimum Review Count",
        min_value=int(df['review_count'].min()),
        max_value=int(df['review_count'].max()),
        value=int(df['review_count'].min()),
        step=10
    )
    
    # Apply filters
    filtered_df = df[
        (df['avg_sentiment'] >= min_sentiment) & 
        (df['review_count'] >= min_reviews)
    ]
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Games",
            len(filtered_df),
            delta=len(filtered_df) - len(df) if len(filtered_df) != len(df) else None
        )
    
    with col2:
        avg_sentiment = filtered_df['avg_sentiment'].mean()
        st.metric(
            "Average Sentiment",
            f"{avg_sentiment:.3f}",
            delta=f"{avg_sentiment - df['avg_sentiment'].mean():.3f}" if len(filtered_df) != len(df) else None
        )
    
    with col3:
        total_reviews = filtered_df['review_count'].sum()
        st.metric(
            "Total Reviews",
            f"{total_reviews:,}",
            delta=f"{total_reviews - df['review_count'].sum():,}" if len(filtered_df) != len(df) else None
        )
    
    with col4:
        avg_positive_ratio = filtered_df['positive_ratio'].mean()
        st.metric(
            "Avg Positive Ratio",
            f"{avg_positive_ratio:.3f}",
            delta=f"{avg_positive_ratio - df['positive_ratio'].mean():.3f}" if len(filtered_df) != len(df) else None
        )
    
    # Charts
    st.header("📊 Analytics Dashboard")
    
    # Row 1: Distribution and Scatter plot
    col1, col2 = st.columns(2)
    
    with col1:
        sentiment_dist_fig = create_sentiment_distribution_chart(filtered_df)
        st.plotly_chart(sentiment_dist_fig, use_container_width=True)
    
    with col2:
        scatter_fig = create_sentiment_vs_reviews_scatter(filtered_df)
        st.plotly_chart(scatter_fig, use_container_width=True)
    
    # Row 2: Top games charts
    col1, col2 = st.columns(2)
    
    with col1:
        top_sentiment_fig = create_top_games_chart(filtered_df, 'avg_sentiment', 10)
        st.plotly_chart(top_sentiment_fig, use_container_width=True)
    
    with col2:
        top_reviews_fig = create_top_games_chart(filtered_df, 'review_count', 10)
        st.plotly_chart(top_reviews_fig, use_container_width=True)
    
    # Data table
    st.header("📋 Game Recommendations Table")
    
    # Sort options
    sort_by = st.selectbox(
        "Sort by:",
        ['avg_sentiment', 'positive_ratio', 'review_count', 'total_reviews'],
        index=0
    )
    
    sort_order = st.radio("Sort order:", ['Descending', 'Ascending'], index=0)
    ascending = sort_order == 'Ascending'
    
    # Display sorted table
    sorted_df = filtered_df.sort_values(sort_by, ascending=ascending)
    
    st.dataframe(
        sorted_df.round(3),
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv = sorted_df.to_csv(index=False)
    st.download_button(
        label="📥 Download filtered data as CSV",
        data=csv,
        file_name="gamesphere_recommendations.csv",
        mime="text/csv"
    )
    
    # Footer
    st.markdown("---")
    st.markdown("**GameSphere Steam Recommender** - Powered by Apache Spark, MLflow, and Streamlit")

if __name__ == "__main__":
    main()
