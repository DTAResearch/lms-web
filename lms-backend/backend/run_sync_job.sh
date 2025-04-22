#!/bin/bash

# ----- Configuration -----
LOG_FILE="/var/log/cronjobs/sync_jobs.log"
MAX_ATTEMPTS=3
RETRY_DELAY=5

# ----- Logging Functions -----
log() {
    local message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$message"  # Gửi trực tiếp ra stdout
    echo "$message" >> "$LOG_FILE"  # Ghi vào file nếu cần
}

log_header() {
    log "===== $1 ====="
}

# ----- Environment Setup -----
log_header "STARTING SYNC JOB"

# Load environment
source /etc/environment
log "Environment loaded"

# Debug info
log "PATH: $PATH"
log "Python: $(which python3)"
log "Python version: $(python3 --version)"

# ----- Job Runner -----
run_job() {
    local job_name=$1
    local attempt=1
    
    while [ $attempt -le $MAX_ATTEMPTS ]; do
        log "Running $job_name (Attempt $attempt/$MAX_ATTEMPTS)"
        
        # Chạy job và gửi output trực tiếp ra stdout
        if python3 "/app/app/jobs/$job_name.py" 2>&1; then
            log "✅ $job_name succeeded"
            return 0
        fi
        
        attempt=$((attempt + 1))
        [ $attempt -le $MAX_ATTEMPTS ] && sleep $RETRY_DELAY
    done
    
    log "❌ $job_name failed after $MAX_ATTEMPTS attempts"
    return 1
}

# ----- Main Execution -----
log_header "SYNC PROCESS STARTED"

final_status=0
for job in "sync_user" "sync_model" "sync_chat"; do
    if ! run_job "$job"; then
        final_status=1
    fi
done

if [ $final_status -eq 0 ]; then
    log_header "✅ ALL JOBS COMPLETED SUCCESSFULLY"
else
    log_header "⚠️ SOME JOBS FAILED"
fi

exit $final_status