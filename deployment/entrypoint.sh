#!/bin/bash

# Fix permissions cho mounted volumes
echo "🔧 Fixing permissions for mounted volumes..."

# Tạo directory nếu chưa có
mkdir -p /app/data/agent_data

# Fix ownership và permissions
sudo chown -R appuser:appuser /app/data/agent_data 2>/dev/null || true
chmod -R 755 /app/data/agent_data 2>/dev/null || true

echo "✅ Permissions fixed successfully"

# Chạy ứng dụng chính
echo "🚀 Starting Streamlit application..."
exec streamlit run main.py --server.address 0.0.0.0 --server.enableCORS false --server.enableXsrfProtection false
