#!/bin/bash
uv run alembic upgrade head
uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
