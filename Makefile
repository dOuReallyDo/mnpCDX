.PHONY: install test lint run-api run-dashboard

install:
	pip install -e .[dev]

test:
	pytest -q

lint:
	ruff check src tests

run-api:
	mnp-cdx api --host 0.0.0.0 --port 8080

run-dashboard:
	mnp-cdx dashboard
