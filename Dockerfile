FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN --mount=type=bind,source=requirements.txt,target=/app/requirements.txt \
    pip install --no-cache-dir --requirement /app/requirements.txt

COPY prestart.sh /app/prestart.sh
COPY app /app

ENV PYTHONPATH="$PYTHONPATH:/app"

ENV CACHE_EXPIRY=3600
ENV REDIS_HOST="localhost"
