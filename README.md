# 👟 Vinted Shoe Condition Detector — Full Stack

## Architecture

```
┌──────────────────────┐  HTTP   ┌──────────────────────┐
│  Streamlit Frontend  │ ──────► │  FastAPI Backend      │
│  localhost:8501      │         │  localhost:8000       │
└──────────────────────┘         └──────────────────────┘
         Both inside Docker Compose
```

## API Endpoints

| Method | Endpoint | What it does |
|--------|----------|-------------|
| GET | /health | Check backend is running |
| GET | /listings | Get all listings |
| POST | /listings | Create new listing |
| DELETE | /listings/{id} | Delete listing |
| POST | /listings/{id}/like | Like a listing |
| POST | /predict | Upload image → AI prediction |

## Setup

```bash
# 1. Copy your model into backend folder
cp best_model.keras backend/best_model.keras

# 2. Build and run everything
docker-compose up --build

# 3. Open
# Frontend:  http://localhost:8501
# API docs:  http://localhost:8000/docs
```
