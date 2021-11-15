clean:
	rm -rf .venv day-summary *.checkpoint .pytest_cache .coverage

init: clean
	pip install pipenv
	pipenv install --dev
	pre-commit install

test:
	pipenv run python -m pytest


# CI/CD
ci-setup:
	pip install pipenv
	pipenv install --dev

ci-test:
	pipenv run python -m pytest