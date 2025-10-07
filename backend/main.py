from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pandas as pd
import os

app = FastAPI()

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to the local Parquet file
PARQUET_PATH = os.path.join(os.path.dirname(__file__), '../final_recommendations.parquet')

# Load data once at startup
try:
    df = pd.read_parquet(PARQUET_PATH)
except Exception as e:
    df = None
    print(f"Error loading Parquet: {e}")

@app.get("/recommendations/{author_index}")
def get_recommendations(author_index: int):
    if df is None:
        raise HTTPException(status_code=500, detail="Data not loaded.")
    user_recs = df[df['author_index'] == author_index]
    if user_recs.empty:
        raise HTTPException(status_code=404, detail="No recommendations found for this user.")
    # Convert to dict, sort by predicted_rating desc
    result = user_recs.sort_values(by="predicted_rating", ascending=False).to_dict(orient="records")
    return {"recommendations": result}

@app.get("/sentiment-leaderboard")
def sentiment_leaderboard():
    if df is None:
        raise HTTPException(status_code=500, detail="Data not loaded.")
    # Group by app_name, get mean percent_positive, sort desc, top 20
    leaderboard = (
        df.groupby("app_name").agg({
            "percent_positive": "mean",
            "avg_sentiment_score": "mean",
            "predicted_rating": "mean"
        })
        .reset_index()
        .sort_values(by="percent_positive", ascending=False)
        .head(20)
    )
    return {"leaderboard": leaderboard.to_dict(orient="records")} 