FROM python:3.12-slim AS builder

WORKDIR /app

# Cài đặt các build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Tạo virtualenv để cô lập dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy và cài đặt requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime - chỉ copy những gì cần thiết
FROM python:3.12-slim

WORKDIR /app

# Cài đặt chỉ runtime dependencies cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* && \
    useradd -m appuser

# Copy virtualenv từ builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Thiết lập user không có quyền root
USER appuser

# Copy code application
COPY --chown=appuser:appuser . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]