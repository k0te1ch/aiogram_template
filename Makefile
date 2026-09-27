.PHONY: install run test lint format check hooks bump

install:
	poetry install
	poetry run pre-commit install --hook-type pre-commit --hook-type commit-msg

run:
	poetry run python cli.py run

test:
	poetry run pytest

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

check:
	poetry run pre-commit run --all-files

bump:
	poetry run cz bump
	git push --follow-tags
