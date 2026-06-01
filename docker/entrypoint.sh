#!/bin/sh

set -e

alembic upgrade head

if [ -z "$FASTID_GUNICORN_WORKERS" ]; then
    CPU_COUNT=$(nproc --all 2>/dev/null || grep -c ^processor /proc/cpuinfo 2>/dev/null || echo 1)
    WORKERS=$((CPU_COUNT * 2 + 1))
    [ "$WORKERS" -gt 16 ] && WORKERS=16
else
    WORKERS=$FASTID_GUNICORN_WORKERS
fi

APP=${FASTID_GUNICORN_APP:-fastid.core.app:core_app}
WORKER_CLASS=${FASTID_GUNICORN_WORKER_CLASS:-fastid.core.workers.MyUvicornWorker}
BIND=${FASTID_GUNICORN_BIND:-0.0.0.0:8000}
BACKLOG=${FASTID_GUNICORN_BACKLOG:-2048}
TIMEOUT=${FASTID_GUNICORN_TIMEOUT:-30}
GRACEFUL_TIMEOUT=${FASTID_GUNICORN_GRACEFUL_TIMEOUT:-10}
KEEP_ALIVE=${FASTID_GUNICORN_KEEP_ALIVE:-5}

echo "Starting Gunicorn with the following configuration:"
echo "  Workers: $WORKERS"
echo "  Worker Class: $WORKER_CLASS"
echo "  App: $APP"
echo "  Bind: $BIND"
echo "  Backlog: $BACKLOG"
echo "  Timeout: $TIMEOUT"
echo "  Graceful Timeout: $GRACEFUL_TIMEOUT"
echo "  Keep Alive: $KEEP_ALIVE"

exec gunicorn \
    -w "$WORKERS" \
    -k fastid.core.workers.MyUvicornWorker \
    "$APP" \
    -b "$BIND" \
    --backlog "$BACKLOG" \
    --timeout "$TIMEOUT" \
    --graceful-timeout "$GRACEFUL_TIMEOUT" \
    --keep-alive "$KEEP_ALIVE" \
    "$@"
