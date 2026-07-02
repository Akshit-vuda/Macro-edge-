.PHONY: up test lint

up:
	docker compose up --build

test:
	python -m pytest

lint:
	python -m flake8 backend config main.py prefect_worker.py tests
