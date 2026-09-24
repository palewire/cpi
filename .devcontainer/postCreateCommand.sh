#!/bin/sh
set -eu
uv sync --all-groups --locked
uv run --no-env-file pre-commit install --install-hooks
