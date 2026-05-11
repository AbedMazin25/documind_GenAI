.PHONY: dev test lint migrate build clean

dev:
	docker compose up -d
	uvicorn app.main:app --reload --port 8000

test:
	pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	ruff check app/ tests/
	mypy app/ --ignore-missing-imports

migrate:
	alembic upgrade head

rollback:
	alembic downgrade -1

build:
	docker compose build

push:
	docker compose push

clean:
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

fe-dev:
	cd frontend && npm run dev

fe-build:
	cd frontend && npm run build

logs:
	docker compose logs -f backend worker
