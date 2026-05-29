FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

COPY services/worker/pyproject.toml services/worker/
RUN pip install --no-cache-dir -e services/worker

COPY services/worker/ services/worker/
COPY packages/ packages/

RUN mkdir -p data/outputs

WORKDIR /app/services/worker

CMD ["rq", "worker", "tabsnap", "--url", "redis://redis:6379/0"]
