# Vanilla Collection - Production Dockerfile
# Multi-stage build for optimized image size

# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash vanilla

# Copy installed packages from builder
COPY --from=builder /root/.local /home/vanilla/.local

# Make sure scripts in .local are usable
ENV PATH=/home/vanilla/.local/bin:$PATH

# Copy application code
COPY --chown=vanilla:vanilla vanilla_collection/ ./vanilla_collection/
COPY --chown=vanilla:vanilla pyproject.toml ./

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000

# Switch to non-root user
USER vanilla

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "-m", "vanilla_collection"]
