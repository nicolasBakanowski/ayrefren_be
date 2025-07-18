#!/bin/sh
set -e

python scripts/wait_for_db.py
alembic upgrade head
python scripts/init_db.py

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
