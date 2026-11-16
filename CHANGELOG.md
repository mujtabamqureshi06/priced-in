# Changelog

All notable changes are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Repository scaffold: `src/` package layout, uv and hatchling packaging, ruff, mypy (strict), pytest with coverage, pre-commit, GitHub Actions CI on Python 3.11 and 3.12.
- Project documents: README, licence, citation file, contributing guide, roadmap, project state, methodology and calibration outlines, sources register.
- Founding decision records 0001 to 0012.
- Decision records 0013 (stage-transition priors) and 0014 (producing-royalty controls; amends 0008), made by the Independent Decision Maker.
- Priors registry: `data/priors.yaml` and a validating loader in `pricedin.priors`. Entries without a source, location, units or status are rejected; secondary-source entries must carry a flag. First entries: `stage.pfs_to_fs`, `stage.fs_to_build`.
