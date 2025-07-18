#!/bin/sh
set -e

# If the first argument is "pytest" we execute the tests directly and skip the
# usual startup steps for the API server. This allows commands such as:
#
#   docker compose -f docker-compose.dev.yml run --rm web pytest
#
# to work without uvicorn complaining about unknown options like "--cov".
if [ "$1" = "pytest" ]; then
    shift
    exec pytest "$@"
fi

python -m scripts.wait_for_db
alembic upgrade head
python -m scripts.init_db

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
