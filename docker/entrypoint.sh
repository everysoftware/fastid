#!/bin/sh

set -e

alembic upgrade head

if [ -z "$FASTID_GUNICORN_WORKERS" ]; then
    CPU_COUNT=$(nproc --all 2>/dev/null || grep -c ^processor /proc/cpuinfo 2>/dev/null || echo 1)
    WORKERS=$CPU_COUNT
else
    WORKERS=$FASTID_GUNICORN_WORKERS
fi

APP=${FASTID_GUNICORN_APP:-fastid.core.app:core_app}
WORKER_CLASS=${FASTID_GUNICORN_WORKER_CLASS:-fastid.core.workers.MyUvicornWorker}
WORKER_CONNECTIONS=${FASTID_GUNICORN_WORKER_CONNECTIONS:-1000}
BIND=${FASTID_GUNICORN_BIND:-0.0.0.0:8000}
BACKLOG=${FASTID_GUNICORN_BACKLOG:-2048}
TIMEOUT=${FASTID_GUNICORN_TIMEOUT:-30}
GRACEFUL_TIMEOUT=${FASTID_GUNICORN_GRACEFUL_TIMEOUT:-10}
KEEP_ALIVE=${FASTID_GUNICORN_KEEP_ALIVE:-5}
MAX_REQUESTS=${FASTID_GUNICORN_MAX_REQUESTS:-10000}
MAX_REQUESTS_JITTER=${FASTID_GUNICORN_MAX_REQUESTS_JITTER:-1000}

echo "Starting Gunicorn with the following configuration:"
echo "  Workers: $WORKERS"
echo "  Worker Class: $WORKER_CLASS"
echo "  Worker Connections: $WORKER_CONNECTIONS"
echo "  App: $APP"
echo "  Bind: $BIND"
echo "  Backlog: $BACKLOG"
echo "  Timeout: $TIMEOUT"
echo "  Graceful Timeout: $GRACEFUL_TIMEOUT"
echo "  Keep Alive: $KEEP_ALIVE"
echo "  Max Requests: $MAX_REQUESTS"
echo "  Max Requests Jitter: $MAX_REQUESTS_JITTER"

exec gunicorn \
    -w "$WORKERS" \
    -k "$WORKER_CLASS" \
    "$APP" \
    -b "$BIND" \
    --worker-connections "$WORKER_CONNECTIONS" \
    --backlog "$BACKLOG" \
    --timeout "$TIMEOUT" \
    --graceful-timeout "$GRACEFUL_TIMEOUT" \
    --keep-alive "$KEEP_ALIVE" \
    --max-requests "$MAX_REQUESTS" \
    --max-requests-jitter "$MAX_REQUESTS_JITTER" \
    --preload \
    "$@"
