FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock alembic.ini ./

FROM base AS dev

RUN uv pip install . --group dev --system

COPY . .

CMD sh -c "alembic upgrade head && \
           uvicorn auth.main:app --host 0.0.0.0 --port 8000 --reload"

FROM base AS prod

ENV PYTHONOPTIMIZE=1

RUN uv pip install . --system

COPY . .

CMD sh -c "alembic upgrade head && \
           gunicorn auth.main:app \
           --workers 2 \
           --worker-class uvicorn.workers.UvicornWorker \
           --bind 0.0.0.0:8000 \
           --timeout 60"