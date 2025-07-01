#!/bin/sh
# AWS Free Tier Optimized Entrypoint Script

set -e

echo "🚀 Starting Agent Education - AWS Free Tier Mode"

# Check if running in lightweight mode
if [ "$AWS_LIGHTWEIGHT_MODE" = "true" ]; then
    echo "⚡ Lightweight mode enabled - optimizing for AWS Free Tier"

    # Set memory-efficient Python settings
    export PYTHONOPTIMIZE=1
    export PYTHONDONTWRITEBYTECODE=1
    export PYTHONUNBUFFERED=1

    # Limit Python memory usage
    export MALLOC_TRIM_THRESHOLD_=100000
    export MALLOC_MMAP_THRESHOLD_=100000

    # Apply lightweight patches
    echo "🔧 Applying AWS Free Tier patches..."
    python /app/lightweight_retrieve_patch.py
fi

# Create necessary directories
mkdir -p /app/data/agent_data
mkdir -p /app/logs

# Set proper permissions
chmod -R 755 /app/data

# Health check function
health_check() {
    echo "🔍 Performing health check..."
    if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        echo "✅ Application is healthy"
        return 0
    else
        echo "❌ Application health check failed"
        return 1
    fi
}

# Graceful shutdown function
shutdown() {
    echo "🛑 Received shutdown signal, gracefully stopping..."
    if [ ! -z "$STREAMLIT_PID" ]; then
        kill -TERM "$STREAMLIT_PID"
        wait "$STREAMLIT_PID"
    fi
    echo "✅ Shutdown complete"
    exit 0
}

# Set up signal handlers
trap shutdown SIGTERM SIGINT

echo "🌐 Starting Streamlit application..."

# Start Streamlit with optimized settings for AWS Free Tier
streamlit run gui/gui.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --server.maxUploadSize=50 \
    --server.maxMessageSize=50 \
    --logger.level=warning \
    --browser.gatherUsageStats=false \
    --global.developmentMode=false &

STREAMLIT_PID=$!

# Wait for application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Perform initial health check
if health_check; then
    echo "🎉 Application started successfully!"
else
    echo "💥 Application failed to start properly"
    exit 1
fi

# Keep the script running and wait for the Streamlit process
wait "$STREAMLIT_PID"
