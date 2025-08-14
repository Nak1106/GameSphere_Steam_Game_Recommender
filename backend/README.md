# Backend - FastAPI API

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- The API will be available at http://localhost:8000
- Make sure `../final_recommendations.parquet` exists relative to the backend folder. 