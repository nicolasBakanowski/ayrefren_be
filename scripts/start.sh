#!/bin/sh
set -e

python -m scripts.wait_for_db
alembic upgrade head
python -m scripts.init_db

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
