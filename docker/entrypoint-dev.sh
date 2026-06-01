#!/bin/sh

set -e

poetry run alembic upgrade head

APP=${FASTID_UVICORN_APP:-fastid.core.app:core_app}
HOST=${FASTID_UVICORN_HOST:-0.0.0.0}
PORT=${FASTID_UVICORN_PORT:-8000}
RELOAD=${FASTID_UVICORN_RELOAD:-1}

echo "Starting Uvicorn with the following configuration:"
echo "  App: $APP"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Reload: $RELOAD"

if [ "$RELOAD" -eq 1 ]; then
    RELOAD="--reload"
else
    RELOAD=""
fi

exec poetry run uvicorn "$APP" --host "$HOST" --port "$PORT" $RELOAD "$@"
