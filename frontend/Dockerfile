# --- BUILD STAGE ---
FROM python:3.11-slim AS builder

# Set build environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Install uv for fast dependency management
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir uv

# Copy only dependency files first for caching
COPY pyproject.toml uv.lock README.md /app/

# Synchronize dependencies (excludes dev dependencies)
RUN uv sync --frozen --no-dev --no-install-project

# --- RUNTIME STAGE ---
FROM python:3.11-slim

# Set runtime environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

WORKDIR /app

# Copy the pre-installed virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy the rest of the application
COPY . /app

# Expose Streamlit port
EXPOSE 8501

# Run the dashboard protocol
CMD ["streamlit", "run", "Home.py"]
