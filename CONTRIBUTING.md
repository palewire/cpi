# Contributing

## Set up a checkout

Install the locked development environment and pre-commit hooks:

```sh
make bootstrap
uv run --no-env-file pre-commit install --install-hooks
```

Use these commands while working:

```sh
make check     # Ruff, ty, dependency, and workflow checks
make test      # Test suite with coverage
make verify    # Checks, tests, package build, and documentation build
```

`make format` changes Python files. `make hooks` runs all hooks and may also
modify files. Review the resulting diff before committing.

The test suite is run on Python 3.9 through 3.12 and is also checked with
Conda. Keep these compatibility targets in mind when changing dependencies or
Python syntax.

## CPI data updates

The monthly BLS refresh changes generated data and test expectations. Follow
[the monthly data update skill](.agents/skills/monthly-cpi-data-update/SKILL.md)
for the sequence and review steps. Do not refresh the database or generated
notebook outputs as part of unrelated changes.

## Documentation

Documentation source is in `docs/src/`. Build it with `make docs-check`; run
`make linkcheck` to check external links.

## Pull requests

Describe the user-facing change, compatibility impact, and validation in the
pull request. Update `CHANGELOG.md` for user-facing, compatibility, or security
changes. Keep generated CPI data and notebook changes focused on an authorized
data refresh.
