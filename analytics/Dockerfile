# Analytics service (A/B assignment + event store + metrics API).
# Build context is this directory (analytics/).
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    AB_DB_PATH=/data/ab_events.sqlite

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && mkdir -p /data

COPY . ./analytics/

EXPOSE 8000
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:8000", "analytics.app:app"]
