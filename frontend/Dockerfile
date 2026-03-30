# --- BUILD STAGE ---
FROM python:3.12-slim AS builder

# Set build environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Install uv binary from source image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install essential build dependencies (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency files first for caching
COPY pyproject.toml uv.lock /app/

# Synchronize dependencies with build caching
RUN uv sync --frozen --no-dev --no-install-project

# --- RUNTIME STAGE ---
FROM python:3.12-slim

# Set runtime environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

WORKDIR /app

# Create a non-root user for security
RUN groupadd -r streamlit && useradd -r -g streamlit streamlit \
    && chown -R streamlit:streamlit /app

# Copy the pre-installed virtual environment from builder
COPY --from=builder --chown=streamlit:streamlit /app/.venv /app/.venv

# Copy the application code
COPY --chown=streamlit:streamlit . /app

# Switch to non-root user
USER streamlit

# Expose Streamlit port
EXPOSE 8501

# Healthcheck for orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the dashboard protocol
ENTRYPOINT ["streamlit", "run"]
CMD ["Home.py"]
