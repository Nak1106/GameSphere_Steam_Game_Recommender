# GameSphere Full-Stack App

This project provides a full-stack web app for Steam game recommendations and sentiment analytics.

## Structure

- `backend/` — FastAPI backend serving recommendations and leaderboard from Parquet
- `frontend/` — React app (Vite) for user interface

## Quick Start

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- Make sure `final_recommendations.parquet` exists in the project root.

### 2. Frontend (React)

```bash
cd frontend
npm install
npm run dev
```
- App runs at http://localhost:5173
- Backend API must be running at http://localhost:8000

## Features
- Personalized game recommendations by author_index
- Sentiment leaderboard for top 20 games
- All data served from local Parquet file (no database required)

## Dependencies
- `pandas`
- `pyarrow`
- `fastapi`
- `uvicorn`
