FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy all source files first (needed for hatchling build)
COPY . .

# Install dependencies
RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["bash", "scripts/start.sh"]
