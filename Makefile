APP_PATH = app
LOGS_SINCE = 10m

.PHONY: deps
deps:
	docker-compose up db redis -d

.PHONY: deps
	uvicorn $(APP_PATH):app --host 0.0.0.0 --port 8000

.PHONY: up
up:
	docker-compose up --build -d

.PHONY: up-prod
up-prod:
	docker-compose -f docker-compose.yml -f docker-compose-prod.yml up --build -d

.PHONY: test
test: deps
	pytest . -s -v

.PHONY: stop
stop:
	docker-compose stop

.PHONY: restart
restart:
	docker-compose restart

.PHONY: format
format:
	ruff format .

.PHONY: lint
lint:
	echo "Running ruff linter (isort, flake, pyupgrade, etc. replacement)..."
	ruff check . --fix
	echo "Running ruff formatter (black replacement)..."
	ruff format .
	echo "Running codespell to find typos..."
	codespell .

.PHONY: static
static:
	echo "Running mypy..."
	mypy .
	echo "Running bandit..."
	bandit -c pyproject.toml -r app

.PHONY: check
check:
	pre-commit run

.PHONY: generate
generate: deps
	alembic revision -m "$(NAME)" --autogenerate
	alembic upgrade head
	alembic downgrade -1
	alembic upgrade head
	alembic downgrade -1

PHONY: upgrade
upgrade: deps
	alembic upgrade head

PHONY: downgrade
downgrade: deps
	alembic downgrade -1

# Windows only
PHONY: kill
kill:
	TASKKILL /F /IM python.exe
