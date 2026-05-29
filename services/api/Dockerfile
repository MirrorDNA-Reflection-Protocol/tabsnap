FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

COPY services/api/pyproject.toml services/api/
RUN pip install --no-cache-dir -e services/api

COPY services/api/ services/api/
COPY packages/ packages/

RUN mkdir -p data/uploads data/outputs

WORKDIR /app/services/api

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
