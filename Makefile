clean:
	rm -rf .venv day-summary *.checkpoint .pytest_cache .coverage

init: clean
	pip install pipenv
	pipenv install
	pre-commit install

test:
	pipenv run python -m pytest


# CI/CD
ci-setup:
	pip install pipenv
	pipenv install

ci-test:
	pipenv run python -m pytest