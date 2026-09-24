---
name: monthly-cpi-data-update
description: Refresh this repository's CPI data from BLS, regenerate its tracked outputs, and update the monthly test expectations. Use for the recurring monthly CPI data maintenance workflow in this repo.
---

# Monthly CPI data update

Use this skill when updating the BLS data and generated outputs for the cpi project. The repository's Makefile, downloader, notebook, and tests define the workflow; keep the refresh consistent with those sources.

## Before refreshing

1. Work from the repository's main branch. Check git status --short --branch and preserve any uncommitted user changes. If the checkout is clean and behind origin/main, fast-forward it before starting.
2. Read the update and test targets in Makefile and check the monthly constants at the top of tests/test_input.py.
3. The local database cpi/cpi.db is ignored by Git. make update clears and rebuilds its tables from BLS downloads, then executes notebooks/analysis.ipynb and sample.py. It needs network access and may take several minutes. Do not delete or overwrite unrelated local files.
4. If the database is incomplete and package import fails before the update command starts, inspect the local schema and diagnose the cause. Deleting cpi/cpi.db is outside the normal Makefile sequence; do it only when the user has authorized a rebuild. When the database is absent, package import may bootstrap a download before python -m cpi.download runs its own update, so the first run can download twice.

## Refresh and update expectations

1. Run make update and let it finish. If it fails, diagnose the cause before proceeding; do not silently skip notebook or sample generation.
2. Run make test before changing expected values. The monthly assertions may fail because the expected month and CPI values are intentionally pinned in the test file. Inspect the failure output and confirm each discrepancy is explained by the refreshed database. Treat unrelated failures as problems to investigate, not stale expectations.
3. If test failures do not make the latest month and values clear, read them from the refreshed database through the public API. For example, run:
   pipenv run python -c 'from datetime import date; import cpi; print(cpi.LATEST_MONTH); print(cpi.inflate(100, date(1950, 1, 1))); print(cpi.inflate(100, date(1950, 1, 1), series_id="CUSR0000SA0"))'
4. Update only the monthly constants at the top of tests/test_input.py from the refreshed database/test output:
   - LATEST_MONTH
   - LATEST_MONTH_1950_ALL_ITEMS
   - LATEST_MONTH_1950_CUSR0000SA0
5. Leave annual constants alone unless annual CPI data or its tested values changed. Do not round or estimate the expected values; use the precise actual values used by the tests.
6. Run make test again. Continue only when the suite passes; note any expected stale-data warning separately from failures.
7. Run the configured pre-commit hooks on the changed files, then review git diff --check, git status, and the full diff. Confirm that generated changes under data/ and notebooks/ are relevant to the refresh and that no SQLite database, cache, coverage file, or build artifact is staged.

## Finish and release

- Summarize the refreshed data month, changed outputs, and verification results.
- Commit and push only when the user has asked for those actions or clearly authorized them for this refresh. Keep the update commit focused on data outputs and test expectations.
- A PyPI release is a separate action. This project derives versions from vMAJOR.MINOR.PATCH Git tags; pushing a tag starts CI and can publish to PyPI. Do not create or move a tag unless the user explicitly requests a release. Do not report a release as published until the tagged CI workflow finishes successfully.
- If CI fails linting, inspect the job log and compare its Ruff version with the version pinned in .pre-commit-config.yaml. Keep the CI Ruff version aligned with the repository's configured version rather than broadening a data refresh into unrelated reformatting.
