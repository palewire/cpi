# Agent Guide

## Project

`cpi` is a Python library and command-line tool for looking up U.S. Bureau of Labor Statistics Consumer Price Index values and adjusting dollar amounts for inflation. It reads data from a local SQLite database built from BLS tables. The `inflate` command is exposed through `cpi.cli:inflate`.

## Setup and checks

- Python 3.9 through 3.12 are supported. The development environment defaults to Python 3.13, configured in `.python-version`.
- Install the exact locked development environment with `make bootstrap` (`uv sync --all-groups --locked`).
- Use `make check` for Ruff lint/format and mypy checks, `make test` for the pytest suite, and `make verify` for checks, tests, and package build validation.
- Use `make format` only when formatting source changes is intended. `make hooks` runs all pre-commit hooks and may modify files.
- Keep Ruff pinned in `pyproject.toml`, `.pre-commit-config.yaml`, and CI aligned. Upgrade it deliberately and review any newly reported findings rather than letting CI select an unpinned release.

## Data updates

- `make update` runs the BLS downloader, executes `notebooks/analysis.ipynb` in place, and regenerates `sample.py` outputs. It needs network access and may take several minutes.
- The database at `cpi/cpi.db` is ignored by Git. Do not delete or overwrite it unless the user specifically asks for a local data rebuild.
- Monthly refreshes may require updating constants near the top of `tests/test_input.py`. Follow `.agents/skills/monthly-cpi-data-update/SKILL.md` for the full workflow and checks.
- Review generated changes under `data/` and `notebooks/`; do not include unrelated notebook edits, caches, SQLite databases, coverage files, or build artifacts.

## Agent and worktree safety

- Edit only the current checkout. Do not modify the primary checkout or sibling worktrees.
- Avoid broad clean, reset, or delete operations. Do not stop services that may be shared with another checkout or agent.
- Coordinate ownership of shared files such as lockfiles, generated data, notebooks, and snapshots before parallel work.
- Do not hand-edit generated data or notebook outputs; use the documented generator commands.

## Packaging and releases

- Package metadata lives in `pyproject.toml`; versions come from Git tags through `setuptools-scm`.
- `make build` creates and checks source and wheel distributions. Keep package metadata, dependencies, the CLI entry point, and compatibility classifiers aligned.
- Pushing a `vMAJOR.MINOR.PATCH` tag starts the release workflow and may publish the package through PyPI Trusted Publishing. The GitHub workflow must be configured as a trusted publisher for the `cpi` project. Creating or moving tags, publishing releases, or changing deployment settings requires explicit user authorization. Do not report a release as published until its workflow completes successfully.

## Change guidelines

- Keep implementation, tests, packaging, and documentation aligned.
- Add tests for new behavior when appropriate.
- Do not commit local databases, caches, `.venv`, coverage data, or build artifacts.
