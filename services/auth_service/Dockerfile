FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock alembic.ini ./
RUN uv pip install . --group dev --system

CMD ["uvicorn", "auth.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
