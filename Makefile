PY ?= python

.PHONY: install lint format test coverage integration e2e run

install:
	$(PY) -m pip install -r requirements-dev.txt
	$(PY) -m playwright install chromium

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

test:
	$(PY) -m pytest -m "not integration and not e2e"

coverage:
	$(PY) -m pytest -m "not integration and not e2e" --cov --cov-report=term --cov-report=xml --junitxml=report.xml

integration:
	$(PY) -m pytest -m integration

e2e:
	$(PY) -m pytest -m e2e --tracing retain-on-failure

run:
	$(PY) -m uvicorn app.main:app --reload
