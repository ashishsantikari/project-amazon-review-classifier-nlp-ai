# AI Review Intelligence

Monorepo application with Streamlit frontend and FastAPI backend.

## Features
- Marketing landing page with CTA
- Sentiment classification
- Category classification with dice animation
- Blog post generation through OpenAI endpoint
- JSON-driven credits page
- CSRF + rate limiting on blog generation endpoint
- Model lazy loading and auto-unload after 3 minutes idle

## Repository Layout
- `frontend/` Streamlit app
- `backend/` FastAPI app
- `models/` mounted model artifacts directory

## Run With Docker Compose
1. Set OpenAI key in environment or `.env`:
   - `OPENAI_API_KEY=...`
2. Start stack:
   - `docker compose up --build`
3. Access apps:
   - Streamlit: http://localhost:8501
   - FastAPI ReDoc: http://localhost:8000/redoc
   - FastAPI Swagger UI (try out): http://localhost:8000/docs

## Local Development
### Backend
- `cd backend`
- `python -m venv .venv && source .venv/bin/activate`
- `cp .env.example .env` and edit values
- `uv sync`
- `RELOAD=true uv run python main.py`

### Frontend
- `cd frontend`
- `python -m venv .venv && source .venv/bin/activate`
- `pip install -r requirements.txt`
- `streamlit run Home.py`

## Security Controls
- Blog generation requires CSRF token from `GET /csrf-token`
- Blog submission requires matching body/header token
- Blog generation is rate-limited per client id
- OpenAI API key remains backend-only
