#!/bin/bash

# Khởi tạo - hiển thị trên terminal
echo "🚀 Initializing cron environment..."

# Tạo file environment
printenv > /etc/environment

# Fix line endings và cấp quyền
dos2unix /app/run_sync_job.sh
chmod +x /app/run_sync_job.sh

# Khởi động cron với logging đầy đủ ra terminal
echo "📅 Starting cron service with full logging..."
cron -L 15 -f 2>&1