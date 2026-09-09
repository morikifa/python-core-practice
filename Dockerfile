# Multi-stage production-ready Dockerfile for TaskFlow CLI
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Final minimal runtime image
FROM python:3.12-slim AS runner

WORKDIR /app

# Создаём непривилегированного пользователя для безопасности (Security Best Practice)
RUN useradd -m -u 1000 appuser && \
    mkdir -p /home/appuser/.taskflow && \
    chown -R appuser:appuser /home/appuser

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/taskflow /usr/local/bin/taskflow

USER appuser
ENV TASKFLOW_STORAGE_PATH=/home/appuser/.taskflow/tasks.json

ENTRYPOINT ["taskflow"]
CMD ["list"]
