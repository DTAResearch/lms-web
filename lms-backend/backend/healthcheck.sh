#!/bin/bash

# Enhanced health check for cron service
if ! pgrep -x "cron" >/dev/null; then
    echo "🔴 ERROR: Cron service is not running"
    exit 1
fi

# Additional check: verify cron can execute jobs
if [ ! -f /var/log/cronjobs/sync_jobs.log ]; then
    echo "⚠️ WARNING: Cron log file not found"
    exit 1
fi

echo "🟢 OK: Cron service is healthy"
exit 0