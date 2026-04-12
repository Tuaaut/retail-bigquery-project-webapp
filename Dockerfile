FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV DBT_PROFILES_DIR=/app
ENV DBT_TARGET=cloud_run

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY dbt_project.yml .
COPY packages.yml .
COPY profiles.yml .
COPY models ./models
COPY macros ./macros
COPY tests ./tests
COPY seeds ./seeds
COPY target ./target
RUN dbt deps --profiles-dir /app

COPY app ./app

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
