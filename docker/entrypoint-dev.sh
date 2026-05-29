#!/bin/sh

set -e

poetry run alembic upgrade head

# You can put other setup logic here
# Evaluating passed command:
exec poetry run uvicorn "fastid.core.app:core_app" --host 0.0.0.0 --port 8000 --reload "$@"
