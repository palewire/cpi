# Releasing

Package versions are derived from Git tags by `setuptools-scm`. Release tags
use the `vMAJOR.MINOR.PATCH` form. Pushing a tag starts the package publication
workflow; it can publish publicly to the Python Package Index. The workflow uses
PyPI Trusted Publishing with GitHub OIDC, so configure `palewire/cpi` and
`.github/workflows/continuous-deployment.yml` as a trusted publisher for the
`cpi` project before the next release tag is pushed.

## Checklist

- [ ] Confirm `main` contains the intended release changes.
- [ ] Review `CHANGELOG.md` and prepare concise notes for the release.
- [ ] Choose the next version from the current Git tags and published package versions.
- [ ] Run `make verify` and `make linkcheck`.
- [ ] Run `make build` and confirm `twine check` and wheel-content checks pass.
- [ ] Obtain explicit approval before creating or moving a version tag.
- [ ] Create the `vMAJOR.MINOR.PATCH` tag on the intended commit and push it.
- [ ] Confirm the tagged workflow and trusted PyPI publication succeed.
- [ ] Verify the published version and tag point to the intended commit.
- [ ] Confirm the documentation workflow publishes the matching site when deployment is enabled.

Agents may prepare release notes and validate a release, but must not create or
move tags, create GitHub releases, deploy documentation, or publish packages
without explicit human approval.

## Documentation deployment

The docs workflow publishes only when `DOCS_DEPLOY_ENABLED` is set to `true`.
Configure a protected `docs-production` environment, an AWS OIDC role in
`DOCS_AWS_ROLE_ARN`, and `DOCS_AWS_REGION`. Configure `DOCS_AWS_BUCKET` and
`DOCS_AWS_BASE_PATH` as environment secrets.
