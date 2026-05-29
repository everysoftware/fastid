#!/bin/sh

set -e

alembic upgrade head

if [ -z "$WORKERS" ]; then
    CPU_COUNT=$(nproc --all 2>/dev/null || grep -c ^processor /proc/cpuinfo 2>/dev/null || echo 1)
    # Например, 2 воркера на ядро + 1, но не меньше 1
    WORKERS=$((CPU_COUNT * 2 + 1))
    # Ограничим максимум разумным значением, чтобы не перегружать БД
    [ "$WORKERS" -gt 16 ] && WORKERS=16
fi

echo "Using $WORKERS workers"

exec gunicorn -w "$WORKERS" -k fastid.core.workers.MyUvicornWorker "fastid.core.app:core_app" -b 0.0.0.0:8000 "$@"
