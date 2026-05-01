.PHONY: install
install:
	poetry install

.PHONY: lint
lint:
	poetry run mypy .

.PHONY: test
test:
	poetry run pytest

.PHONY: test-with-cov
test-with-cov:
	poetry run pytest --cov=yaml_includes
