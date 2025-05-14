.PHONY: certs
certs:
	mkdir certs
	openssl genrsa -out certs/jwt-private.pem 2048
	openssl rsa -in certs/jwt-private.pem -pubout -out certs/jwt-public.pem

.PHONY: deps
deps:
	docker-compose up db redis -d

.PHONY: up
up:
	docker-compose up --build -d

.PHONY: up-prod
up-prod:
	docker-compose -f docker-compose.yml -f docker-compose-prod.yml up --build -d

.PHONY: test
test: deps
	pytest . -x -s -v --ff

.PHONY: coverage
coverage: deps
	coverage run -m pytest -x --ff
	coverage combine
	coverage report --show-missing --skip-covered --sort=cover --precision=2
	coverage html
	rm .coverage*

.PHONY: stop
stop:
	docker-compose stop

.PHONY: restart
restart:
	docker-compose restart

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
