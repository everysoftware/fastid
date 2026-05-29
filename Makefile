.PHONY: certs
certs:
	mkdir certs
	openssl genrsa -out certs/jwt-private.pem 2048
	openssl rsa -in certs/jwt-private.pem -pubout -out certs/jwt-public.pem

.PHONY: deps
deps:
	docker compose -f docker-compose.dev.yml postgres redis up -d --build --remove-orphans --wait

.PHONY: up
up:
	docker compose -f docker-compose.dev.yml up --build --remove-orphans --wait

.PHONY: up-obs
up-obs:
	docker compose -f docker-compose.dev.yml -f docker-compose.observability.yml up --build --remove-orphans --wait

.PHONY: up-prod
up-prod:
	docker compose -f docker-compose.dev.yml -f docker-compose.prod.yml up --build --remove-orphans --wait

.PHONY: up-prod-obs
up-prod-obs:
	docker compose -f docker-compose.dev.yml -f docker-compose.prod.yml -f docker-compose.observability.yml up --build --remove-orphans --wait

.PHONY: up-example
up-example:
	docker compose -f docker-compose.example.yml up --build --remove-orphans --wait

.PHONY: test
test:
	pytest . -x -s -v --ff -m 'not slow'

.PHONY: testcov
testcov:
	coverage run -m pytest -x --ff -m 'not slow'
	coverage combine
	coverage report --show-missing --skip-covered --sort=cover --precision=2
	coverage html
	rm .coverage*

.PHONY: stop
stop:
	docker compose -f docker-compose.dev.yml stop

.PHONY: down
down:
	docker compose -f docker-compose.dev.yml down

.PHONY: restart
restart:
	docker compose -f docker-compose.dev.yml restart

.PHONY: lint
lint:
	@echo "Running ruff linter (isort, flake, pyupgrade, etc. replacement)..."
	ruff check . --fix
	@echo "Running ruff formatter (black replacement)..."
	ruff format .
	@echo "Running codespell to find typos..."
	codespell .

.PHONY: static
static:
	@echo "Running mypy..."
	mypy .

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
