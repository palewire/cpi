# Repository guide for coding agents

## Project overview

`cpi` is a Python library and command-line tool for looking up U.S. Bureau of Labor Statistics Consumer Price Index values and adjusting dollar amounts for inflation. The package reads its data from a local SQLite database built from BLS tables.

## Development environment

- The project uses Pipenv; `Pipfile` targets Python 3.11.
- `make test` runs the test suite with pytest, xdist, and coverage.
- Run configured hooks with `pipenv run pre-commit run --all-files` when changing project files. The pinned hooks include whitespace and file checks, Ruff, Blacken-docs, pyupgrade, and mypy.
- Use the existing code style and add Python type hints when practical. Keep compatibility with Python 3.9 through 3.12, which are tested in CI.

## CPI data refreshes

- `make update` runs `python -m cpi.download`, executes `notebooks/analysis.ipynb`, and runs `sample.py`. It downloads the current BLS source files, replaces the local SQLite tables, and regenerates tracked data and notebook outputs. It requires network access and can take several minutes.
- The database at `cpi/cpi.db` is ignored by Git. Do not commit it or delete it unless the user specifically asks for a local data rebuild.
- Monthly data refreshes change the `LATEST_MONTH` and related expected values near the top of `tests/test_input.py`. Update those values from the refreshed data, then run `make test` again.
- Review generated changes under `data/` and `notebooks/` after a refresh. Keep the updated outputs needed by the project, and avoid including unrelated notebook edits or local artifacts.
- Annual expectations in the test file should only be changed when annual CPI data changes.

## Release workflow

- Package versions are derived from Git tags by `setuptools_scm`; release tags use the `vMAJOR.MINOR.PATCH` form.
- Pushing a version tag starts the continuous-deployment workflow. It runs linting, typing, tests, builds and checks the package, then publishes to PyPI when the required jobs succeed and the repository's PyPI secret is available.
- Creating and pushing a version tag publishes a public package release. Do this only when the user explicitly requests a release. Do not claim PyPI publication until the tagged workflow completes successfully.

## Scope and safety

- Keep changes focused on the requested work and do not commit local databases, caches, coverage files, or build artifacts.
- Do not push commits, create tags, publish releases, or modify external services unless the user has explicitly requested that action.
