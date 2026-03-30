from __future__ import annotations

import logging
import os
from logging.config import dictConfig


def get_configured_log_level() -> str:
    debug_enabled = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"}
    default_level = "DEBUG" if debug_enabled else "INFO"
    return os.getenv("LOG_LEVEL", default_level).upper()


def setup_logging() -> None:
    configured_level = get_configured_log_level()
    resolved_level = getattr(logging, configured_level, logging.INFO)

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s %(levelname)s %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {
                "level": resolved_level,
                "handlers": ["default"],
            },
            "loggers": {
                "app": {
                    "level": resolved_level,
                    "handlers": ["default"],
                    "propagate": False,
                },
                "uvicorn": {
                    "level": resolved_level,
                    "handlers": ["default"],
                    "propagate": False,
                },
                "uvicorn.error": {
                    "level": resolved_level,
                    "handlers": ["default"],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": resolved_level,
                    "handlers": ["default"],
                    "propagate": False,
                },
            },
        }
    )
