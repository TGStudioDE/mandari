SHELL := /usr/bin/bash
COMPOSE := docker compose

.PHONY: up down logs restart ps build migrate createsuperuser django-shell openapi fmt lint \
	backend-makemigrations ingest-run ai-run

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down -v

logs:
	$(COMPOSE) logs -f | cat

restart:
	$(COMPOSE) restart

ps:
	$(COMPOSE) ps

build:
	$(COMPOSE) build --no-cache

migrate:
	$(COMPOSE) exec backend python manage.py migrate

backend-makemigrations:
	$(COMPOSE) exec backend python manage.py makemigrations

createsuperuser:
	$(COMPOSE) exec backend python manage.py createsuperuser --noinput || true

django-shell:
	$(COMPOSE) exec backend python manage.py shell

openapi:
	$(COMPOSE) exec backend python manage.py spectacular --file /app/docs/api-mvp.yaml || true

fmt:
	$(COMPOSE) exec backend bash -lc "ruff check --select I --fix . && ruff format ."

lint:
	$(COMPOSE) exec backend bash -lc "ruff check ."

ingest-run:
	$(COMPOSE) exec ingest uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

ai-run:
	$(COMPOSE) exec ai uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

test:
	$(COMPOSE) exec backend pytest -q | cat

