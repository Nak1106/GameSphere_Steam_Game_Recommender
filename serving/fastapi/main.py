#!/usr/bin/env python3
"""
GameSphere Steam Recommender - FastAPI Service
REST API for serving game recommendations and sentiment data
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GameSphere API",
    description="Steam Game Recommender API powered by Apache Spark and ML",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class GameRecommendation(BaseModel):
    app_id: str
    avg_sentiment: float
    positive_ratio: float
    review_count: int
    total_reviews: int

class UserRecommendations(BaseModel):
    author_index: int
    recommended_games: List[str]
    recommendation_scores: List[float]

class SentimentLeaderboard(BaseModel):
    games: List[GameRecommendation]
    total_count: int

# Global data storage
recommendations_df = None
user_recommendations_df = None

def load_data():
    """Load recommendation data on startup"""
    global recommendations_df, user_recommendations_df
    
    try:
        # Try to load app recommendations
        app_recs_path = "app_recommendations.parquet"
        if os.path.exists(app_recs_path):
            logger.info(f"Loading app recommendations from {app_recs_path}")
            recommendations_df = pd.read_parquet(app_recs_path)
        else:
            # Try alternative paths
            alt_paths = [
                "../../app_recommendations.parquet",
                "../app_recommendations.parquet"
            ]
            for path in alt_paths:
                if os.path.exists(path):
                    logger.info(f"Loading app recommendations from {path}")
                    recommendations_df = pd.read_parquet(path)
                    break
        
        # Try to load user recommendations
        user_recs_path = "final_recommendations.parquet"
        if os.path.exists(user_recs_path):
            logger.info(f"Loading user recommendations from {user_recs_path}")
            user_recommendations_df = pd.read_parquet(user_recs_path)
        else:
            # Try alternative paths
            alt_paths = [
                "../../final_recommendations.parquet",
                "../final_recommendations.parquet"
            ]
            for path in alt_paths:
                if os.path.exists(path):
                    logger.info(f"Loading user recommendations from {path}")
                    user_recommendations_df = pd.read_parquet(path)
                    break
        
        # Create sample data if files don't exist
        if recommendations_df is None:
            logger.warning("Creating sample app recommendations data")
            recommendations_df = pd.DataFrame({
                'app_id': [f'game_{i}' for i in range(1, 21)],
                'avg_sentiment': [0.6 + (i * 0.02) for i in range(20)],
                'positive_ratio': [0.5 + (i * 0.025) for i in range(20)],
                'review_count': [100 + (i * 50) for i in range(20)],
                'total_reviews': [120 + (i * 60) for i in range(20)]
            })
        
        if user_recommendations_df is None:
            logger.warning("Creating sample user recommendations data")
            user_recommendations_df = pd.DataFrame({
                'user': [i for i in range(10)],
                'recommendations': [
                    [{'item': f'game_{j}', 'rating': 0.8 - (j * 0.1)} for j in range(5)]
                    for i in range(10)
                ]
            })
        
        logger.info(f"Loaded {len(recommendations_df)} app recommendations")
        logger.info(f"Loaded {len(user_recommendations_df)} user recommendation sets")
        
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        # Create minimal fallback data
        recommendations_df = pd.DataFrame({
            'app_id': ['sample_game'],
            'avg_sentiment': [0.75],
            'positive_ratio': [0.8],
            'review_count': [100],
            'total_reviews': [120]
        })
        user_recommendations_df = pd.DataFrame({
            'user': [0],
            'recommendations': [[{'item': 'sample_game', 'rating': 0.8}]]
        })

@app.on_event("startup")
async def startup_event():
    """Load data when the API starts"""
    load_data()

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "message": "GameSphere API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "data_loaded": {
            "app_recommendations": recommendations_df is not None and len(recommendations_df) > 0,
            "user_recommendations": user_recommendations_df is not None and len(user_recommendations_df) > 0
        },
        "counts": {
            "total_games": len(recommendations_df) if recommendations_df is not None else 0,
            "total_users": len(user_recommendations_df) if user_recommendations_df is not None else 0
        }
    }

@app.get("/recommendations/{author_index}", response_model=UserRecommendations, tags=["Recommendations"])
async def get_user_recommendations(author_index: int):
    """Get recommendations for a specific user by author index"""
    if user_recommendations_df is None:
        raise HTTPException(status_code=503, detail="User recommendations data not available")
    
    # Find user recommendations
    user_recs = user_recommendations_df[user_recommendations_df['user'] == author_index]
    
    if user_recs.empty:
        raise HTTPException(status_code=404, detail=f"No recommendations found for user {author_index}")
    
    # Extract recommendations
    recs = user_recs.iloc[0]['recommendations']
    
    if isinstance(recs, list) and len(recs) > 0:
        games = [rec['item'] if isinstance(rec, dict) else str(rec) for rec in recs]
        scores = [rec['rating'] if isinstance(rec, dict) else 0.5 for rec in recs]
    else:
        games = []
        scores = []
    
    return UserRecommendations(
        author_index=author_index,
        recommended_games=games,
        recommendation_scores=scores
    )

@app.get("/sentiment-leaderboard", response_model=SentimentLeaderboard, tags=["Analytics"])
async def get_sentiment_leaderboard(
    limit: int = Query(default=20, ge=1, le=100, description="Number of games to return"),
    min_reviews: int = Query(default=10, ge=0, description="Minimum number of reviews"),
    sort_by: str = Query(default="avg_sentiment", regex="^(avg_sentiment|positive_ratio|review_count)$")
):
    """Get top games ranked by sentiment score"""
    if recommendations_df is None:
        raise HTTPException(status_code=503, detail="Recommendations data not available")
    
    # Filter and sort data
    filtered_df = recommendations_df[recommendations_df['review_count'] >= min_reviews]
    sorted_df = filtered_df.sort_values(sort_by, ascending=False).head(limit)
    
    # Convert to response format
    games = []
    for _, row in sorted_df.iterrows():
        games.append(GameRecommendation(
            app_id=row['app_id'],
            avg_sentiment=float(row['avg_sentiment']),
            positive_ratio=float(row['positive_ratio']),
            review_count=int(row['review_count']),
            total_reviews=int(row['total_reviews'])
        ))
    
    return SentimentLeaderboard(
        games=games,
        total_count=len(filtered_df)
    )

@app.get("/games/{app_id}", response_model=GameRecommendation, tags=["Games"])
async def get_game_details(app_id: str):
    """Get details for a specific game"""
    if recommendations_df is None:
        raise HTTPException(status_code=503, detail="Recommendations data not available")
    
    game_data = recommendations_df[recommendations_df['app_id'] == app_id]
    
    if game_data.empty:
        raise HTTPException(status_code=404, detail=f"Game {app_id} not found")
    
    row = game_data.iloc[0]
    return GameRecommendation(
        app_id=row['app_id'],
        avg_sentiment=float(row['avg_sentiment']),
        positive_ratio=float(row['positive_ratio']),
        review_count=int(row['review_count']),
        total_reviews=int(row['total_reviews'])
    )

@app.get("/stats", tags=["Analytics"])
async def get_statistics():
    """Get overall statistics"""
    if recommendations_df is None:
        raise HTTPException(status_code=503, detail="Recommendations data not available")
    
    return {
        "total_games": len(recommendations_df),
        "average_sentiment": float(recommendations_df['avg_sentiment'].mean()),
        "average_positive_ratio": float(recommendations_df['positive_ratio'].mean()),
        "total_reviews": int(recommendations_df['review_count'].sum()),
        "sentiment_distribution": {
            "high_sentiment": len(recommendations_df[recommendations_df['avg_sentiment'] > 0.7]),
            "medium_sentiment": len(recommendations_df[
                (recommendations_df['avg_sentiment'] >= 0.4) & 
                (recommendations_df['avg_sentiment'] <= 0.7)
            ]),
            "low_sentiment": len(recommendations_df[recommendations_df['avg_sentiment'] < 0.4])
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
