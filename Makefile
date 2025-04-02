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
	ruff check . --fix
	mypy .

.PHONY: fix
fix:
	ruff check . --fix --unsafe-fixes
	ruff format .
	mypy .

PHONY: generate
generate:
	docker-compose up db -d
	alembic revision --autogenerate

PHONY: upgrade
upgrade:
	docker-compose up db -d
	alembic upgrade head

PHONY: downgrade
downgrade:
	docker-compose up db -d
	alembic downgrade -1

# Windows only
PHONY: kill
kill:
	TASKKILL /F /IM python.exe
