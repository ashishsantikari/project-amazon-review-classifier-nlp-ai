import importlib
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from app.logging_config import get_configured_log_level, setup_logging

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")
load_dotenv(PROJECT_ROOT / ".env")

setup_logging()

logger = logging.getLogger(__name__)


def log_runtime_env() -> None:
    if os.getenv("DEBUG_STARTUP_ENV", "false").lower() not in {"1", "true", "yes", "on"}:
        return

    keys = [
        "HOST",
        "PORT",
        "RELOAD",
        "DEBUG",
        "LOG_LEVEL",
        "MODEL_ROOT",
        "MODEL_IDLE_SECONDS",
        "MODEL_MANAGER_VERBOSE",
        "SENTIMENT_MODEL_DIR",
        "CATEGORY_MODEL_DIR",
        "REFERENCE_SENTIMENT_MODEL_ID",
        "FRONTEND_ORIGIN",
        "CSRF_TTL_SECONDS",
        "BLOG_RATE_LIMIT_MAX",
        "BLOG_RATE_LIMIT_WINDOW_SECONDS",
        "OPENAI_MODEL",
    ]
    logger.debug("Runtime environment snapshot start")
    for key in keys:
        logger.debug("ENV %s=%s", key, os.getenv(key, "<unset>"))
    logger.debug("Runtime environment snapshot end")

def create_app():
    return importlib.import_module("app.main").create_app()


def main() -> None:
    import uvicorn

    log_runtime_env()
    app_module = importlib.import_module("app.main")

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload_enabled = os.getenv("RELOAD", "false").lower() in {"1", "true", "yes", "on"}
    log_level = get_configured_log_level().lower()
    app_target = "app.main:app" if reload_enabled else app_module.app
    uvicorn.run(app_target, host=host, port=port, reload=reload_enabled, log_level=log_level)


if __name__ == "__main__":
    main()
