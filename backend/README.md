# Backend API

FastAPI backend for the AI Review Intelligence project.

## Docs and Try-Out
- ReDoc (API reference): http://localhost:8000/redoc
- Swagger UI (interactive try-out): http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

## Local Run (uv)
- Copy `.env.example` to `.env` and fill values as needed.
- `uv sync`
- `RELOAD=true uv run python main.py`

## Debug Run
- `DEBUG=true LOG_LEVEL=debug MODEL_MANAGER_VERBOSE=true RELOAD=true uv run python main.py`

## Logging
- Standard practice used here: one centralized logging config in `app/logging_config.py`, and module-level loggers using `logging.getLogger(__name__)`.
- Optional startup env dump: `DEBUG_STARTUP_ENV=true`

## Main Endpoints
- `GET /health`
- `GET /csrf-token`
- `POST /predict/sentiment`
- `POST /predict/category`
- `POST /generate/blog`
