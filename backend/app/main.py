from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.model_manager import ModelManager
from app.openai_client import BlogGenerator
from app.schemas import (
    BlogRequest,
    BlogResponse,
    CategoryResponse,
    CsrfResponse,
    PredictRequest,
    SentimentPredictRequest,
    SentimentResponse,
)
from app.security import CsrfManager, RateLimiter

APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

# Load backend-first, then project-level .env (without overriding already-set vars).
load_dotenv(BACKEND_DIR / ".env")
load_dotenv(PROJECT_ROOT / ".env")

API_TAGS = [
    {"name": "system", "description": "System and documentation endpoints."},
    {"name": "prediction", "description": "Sentiment and category prediction endpoints."},
    {"name": "content", "description": "Blog generation endpoints with CSRF and rate limiting."},
]

model_root_env = os.getenv("MODEL_ROOT", "/models")
model_root_path = Path(model_root_env)
if not model_root_path.is_absolute():
    model_root_path = (BACKEND_DIR / model_root_path).resolve()

model_manager = ModelManager(
    model_root=str(model_root_path),
    idle_seconds=int(os.getenv("MODEL_IDLE_SECONDS", "180")),
)
csrf_manager = CsrfManager(ttl_seconds=int(os.getenv("CSRF_TTL_SECONDS", "600")))
blog_rate_limiter = RateLimiter(
    max_requests=int(os.getenv("BLOG_RATE_LIMIT_MAX", "5")),
    window_seconds=int(os.getenv("BLOG_RATE_LIMIT_WINDOW_SECONDS", "3600")),
)
blog_generator = BlogGenerator()


@asynccontextmanager
async def lifespan(_: FastAPI):
    stop_event = asyncio.Event()

    async def sweeper() -> None:
        while not stop_event.is_set():
            model_manager.unload_idle_models()
            await asyncio.sleep(30)

    task = asyncio.create_task(sweeper())
    try:
        yield
    finally:
        stop_event.set()
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


app = FastAPI(
    title="ML Engine API",
    version="1.0.0",
    description=(
        "REST API for sentiment prediction, category prediction, and blog generation. "
        "Use ReDoc for endpoint understanding and Swagger UI for interactive try-out."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=API_TAGS,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "*")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "message": "ML Engine API is running",
        "redoc": "/redoc",
        "swagger_ui": "/docs",
        "openapi_json": "/openapi.json",
    }


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/models", tags=["system"])
def get_models() -> dict[str, Any]:
    return model_manager.models_config


@app.get("/csrf-token", response_model=CsrfResponse, tags=["content"])
def csrf_token() -> CsrfResponse:
    token, expires = csrf_manager.issue()
    return CsrfResponse(csrf_token=token, expires_in_seconds=expires)


@app.post("/predict/sentiment", response_model=SentimentResponse, tags=["prediction"])
def predict_sentiment(payload: SentimentPredictRequest) -> SentimentResponse:
    sentiment, confidence, model_name = model_manager.sentiment_predict(
        payload.text,
        model_option=payload.sentiment_model,
    )
    return SentimentResponse(sentiment=sentiment, confidence=confidence, model=model_name)


@app.post("/predict/category", response_model=CategoryResponse, tags=["prediction"])
def predict_category(payload: PredictRequest) -> CategoryResponse:
    category, confidence, model_name = model_manager.category_predict(payload.text)
    return CategoryResponse(category=category, confidence=confidence, model=model_name)


@app.post("/generate/blog", response_model=BlogResponse, tags=["content"])
def generate_blog(
    payload: BlogRequest,
    x_csrf_token: str | None = Header(default=None),
    x_client_id: str | None = Header(default="anonymous"),
) -> BlogResponse:
    if not x_csrf_token or x_csrf_token != payload.csrf_token:
        raise HTTPException(status_code=403, detail="Invalid CSRF token header/body mismatch")

    if not csrf_manager.validate(payload.csrf_token):
        raise HTTPException(status_code=403, detail="Expired or invalid CSRF token")

    allowed, meta = blog_rate_limiter.allow(x_client_id or "anonymous")
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit reached. Try again in about {meta} seconds.",
        )

    blog_text = blog_generator.generate(
        category=payload.category,
        product=payload.product,
        review=payload.review,
    )
    return BlogResponse(blog_post=blog_text)


def create_app() -> FastAPI:
    return app