# Main application service (Flask + Jinja templates).
# Build context is this directory (web/).
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:8080", "fellowship:app"]
