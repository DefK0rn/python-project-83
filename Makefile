install:
	uv sync

dev:
	uv run python init_db.py && uv run flask --debug --app page_analyzer:app run

check:
	uv run ruff check

test-coverage:
	uv run pytest -rs --cov=page_analyzer --cov-report xml

PORT ?= 8000
start:
	uv run python init_db.py && uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app