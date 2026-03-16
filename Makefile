PWD      := $(shell pwd)
PYTHON   := uv run python
PYTEST   := uv run pytest
RUFF     := uv run ruff
PYRIGHT  := uv run pyright

.PHONY: all
all: format lint test


.PHONY: test
test: test-python test-ts

.PHONY: test-python
test-python:
	PYTHONPATH=$(PWD) $(PYTEST)

.PHONY: test-ts
test-ts:
	bun run --cwd runtime test

.PHONY: lint
lint:
	PYTHONPATH=$(PWD) $(RUFF) check
	PYTHONPATH=$(PWD) $(PYRIGHT)

.PHONY: format
format:
	PYTHONPATH=$(PWD) $(RUFF) check --select I --fix
	PYTHONPATH=$(PWD) $(RUFF) format

.PHONY: build
build: build-runtime

.PHONY: build-runtime
build-runtime:
	bun run --cwd runtime build

.PHONY: build-runtime-dev
build-runtime-dev:
	bun run --cwd runtime build:dev

.PHONY: clean
clean: clean-pyc clean-build

.PHONY: clean-pyc
clean-pyc:
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-build
clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf $(MODULE).egg-info/
	rm -rf pip-wheel-metadata/
