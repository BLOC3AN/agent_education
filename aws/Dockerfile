# Multi-stage build for AWS Free Tier optimization
# Stage 1: Build stage
FROM python:3.10-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    build-base

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY aws/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.10-alpine AS runtime

# Metadata
LABEL maintainer="Agent Education Team"
LABEL description="AI Education Agent - AWS Free Tier Optimized"

# Set environment variables for optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_MAX_UPLOAD_SIZE=50 \
    STREAMLIT_SERVER_MAX_MESSAGE_SIZE=50 \
    STREAMLIT_LOGGER_LEVEL=WARNING \
    AWS_LIGHTWEIGHT_MODE=true

# Install only runtime dependencies
RUN apk add --no-cache \
    curl \
    ca-certificates \
    && rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -g 1000 appuser && \
    adduser -D -s /bin/sh -u 1000 -G appuser appuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy only necessary source files
COPY src/ ./src/
COPY gui/ ./gui/
COPY main.py ./
COPY aws/entrypoint.sh /entrypoint.sh

# Create minimal data directory
RUN mkdir -p /app/data/agent_data && \
    chown -R appuser:appuser /app && \
    chmod +x /entrypoint.sh

# Switch to non-root user
USER appuser

# Add local packages to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Expose port
EXPOSE 8501

# Health check with reduced frequency for resource saving
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=2 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["/entrypoint.sh"]
