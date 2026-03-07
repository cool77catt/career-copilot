FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY uv.lock* ./
RUN uv sync --frozen || uv sync

COPY . .

EXPOSE 8000
CMD ["bash", "scripts/run.sh"]
