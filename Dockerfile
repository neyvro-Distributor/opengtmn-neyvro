FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY skills ./skills
COPY assets ./assets

RUN pip install --no-cache-dir . "uvicorn>=0.30,<1"

USER appuser
EXPOSE 10000

CMD ["sh", "-c", "exec uvicorn neyvro.remote_mcp:REMOTE_APP --host 0.0.0.0 --port ${PORT:-10000}"]
