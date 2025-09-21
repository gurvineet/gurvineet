# Multi-stage build for security and size optimization
FROM python:3.11-slim as base

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install security updates and minimal dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with security considerations
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip check

# Production stage
FROM base as production

# Copy application code
COPY src/ ./src/
COPY run_tests.py ./
COPY demo.py ./

# Create data directory with proper permissions
RUN mkdir -p /app/data && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    chmod -R 750 /app/data

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import src.main; print('OK')" || exit 1

# Security labels
LABEL \
    org.opencontainers.image.title="CloudKitchens Kitchen Optimization" \
    org.opencontainers.image.description="Kitchen workflow optimization system" \
    org.opencontainers.image.version="1.0.0" \
    org.opencontainers.image.vendor="CloudKitchens" \
    security.scan="enabled"

# Set secure environment variables
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random

# Expose port (if needed for future web interface)
EXPOSE 8000

# Default command
CMD ["python3", "src/main.py"]