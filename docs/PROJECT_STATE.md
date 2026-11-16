# Project state

Updated: 2026-11-15 by the Mastermind.

## Where we are

Phase 0 (foundation), in progress.

## Done

- Repository scaffold built and checked locally: package layout, uv and hatchling, ruff, mypy strict, pytest, pre-commit, CI workflow for Python 3.11 and 3.12. Lint, types and tests pass.
- Project documents: README, LICENSE, CITATION.cff, CONTRIBUTING, CHANGELOG, ROADMAP, this file, methodology and calibration outlines.
- ADRs 0001 to 0012 (founding decisions).
- `docs/sources.md`: case facts for Osino, South Railroad, Sorby Hills and White Dam verified against issuer releases; calibration sources triaged.

## In progress

- WP 0.3: full texts of Bertisen and Davis (2008) and Suárez Nieto et al. (2024); S&P phase split; Davis (1995) and Iddon (2015).
- Search for clean producing-royalty controls (ADR 0008).

## Blocked

- Push to GitHub: the repository does not exist yet (owner action).
- WP 0.5 hand-filled case templates: need the Osino DFS technical report (July 2023) and the South Railroad PFS technical report (March 2020) from SEDAR+ or company sites, and the Osino circular (March 25, 2024).
- Paywalled papers: need University of Toronto library sign-in (owner action).

## Open questions

- How to set stage-transition priors without a cohort-based source (decision request pending).
- Which two or three producing royalties serve as controls for the buyer's required return (decision request pending).

## Next

1. WP 0.4: priors registry schema and loader, with flagged stage priors.
2. WP 0.5: input template schema; fill Osino and South Railroad once the reports are in hand.
3. Producing-royalty control shortlist.
