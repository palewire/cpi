.DEFAULT_GOAL := help

UV ?= uv
UV_PYTHON ?=
PYTHON_ARG = $(if $(UV_PYTHON),--python $(UV_PYTHON))
RUN = $(UV) run --no-env-file $(PYTHON_ARG)
TEST_ARGS ?=

.PHONY: help bootstrap install install-dev install-test install-docs update test lint format-check format type-check check build docs docs-check linkcheck dependency-check workflow-check manifest-check verify hooks

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_-]+:.*## / {printf "%-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

bootstrap: ## Install all locked dependencies for development
	$(UV) sync --all-groups --locked $(PYTHON_ARG)

install: bootstrap ## Alias for bootstrap

install-dev: ## Install project and development tools
	$(UV) sync --group dev --locked $(PYTHON_ARG)

install-test: ## Install project and test tools
	$(UV) sync --group test --locked $(PYTHON_ARG)

install-docs: ## Install project and documentation tools
	$(UV) sync --group docs --locked $(PYTHON_ARG)

update: ## Refresh BLS data and regenerate the notebook and sample outputs
	$(RUN) python -m cpi.download
	$(RUN) jupyter execute --inplace notebooks/analysis.ipynb
	$(RUN) python sample.py

test: ## Run the test suite with coverage
	$(RUN) pytest -n auto --cov=cpi --cov-report term-missing tests $(TEST_ARGS)

lint: ## Check Python code with Ruff
	$(RUN) ruff check .

format-check: ## Check Python formatting with Ruff
	$(RUN) ruff format --check .

format: ## Format Python code with Ruff
	$(RUN) ruff format .

type-check: ## Check Python types with ty
	$(RUN) ty check cpi

dependency-check: ## Check declared dependencies with Deptry
	$(RUN) deptry cpi --known-first-party cpi

workflow-check: ## Audit GitHub Actions workflows with Zizmor
	$(RUN) zizmor .github/workflows

manifest-check: ## Check source distribution contents
	$(RUN) check-manifest

check: lint format-check type-check dependency-check workflow-check ## Run fast static checks

build: ## Build and validate source and wheel distributions
	rm -rf dist
	$(UV) build --sdist --wheel
	$(RUN) twine check dist/*
	$(RUN) check-wheel-contents dist/*.whl

docs: ## Build HTML documentation
	$(RUN) sphinx-build -M html docs/src docs/_build

docs-check: ## Build documentation and fail on warnings
	$(RUN) sphinx-build -M html docs/src docs/_build -W --keep-going

linkcheck: ## Check documentation links and fail on warnings
	$(RUN) sphinx-build -M linkcheck docs/src docs/_build -W --keep-going

verify: check test manifest-check build docs-check ## Run the local CI checks

hooks: ## Run all pre-commit hooks; hooks may modify files
	$(RUN) pre-commit run --all-files
