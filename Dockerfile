FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml .
RUN pip install --upgrade pip && pip install -e ".[dev]"

COPY . .

RUN mkdir -p /app/logs /app/data

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8001"]
