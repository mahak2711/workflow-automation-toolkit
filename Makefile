.PHONY: dev lint test build up down worker beat

dev:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

lint:
	ruff check .

test:
	pytest tests/ -v

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

worker:
	celery -A workers.celery_app worker -l info -c 4

beat:
	celery -A workers.celery_app beat -l info
