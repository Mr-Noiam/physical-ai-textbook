# Multi-stage Docker build for FastAPI backend
# Optimized for Railway deployment

# Stage 1: Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY ./app ./app
COPY ./scripts ./scripts

# Make sure scripts are on PATH
ENV PATH=/root/.local/bin:$PATH

# Expose port (Railway uses PORT env var)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run FastAPI with Uvicorn
# Use PORT env var (Railway requirement) with fallback to 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
