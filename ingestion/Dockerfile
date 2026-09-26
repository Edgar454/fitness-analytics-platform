FROM python:3.13-slim

WORKDIR /app

RUN python -m pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

RUN uv sync --locked --no-dev

COPY ingestion/ ingestion/

ENTRYPOINT ["python", "-m", "ingestion.src.ingestion.worker.main"]
