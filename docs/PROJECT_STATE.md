# Project state

Updated: 2026-11-16 by the Mastermind.

## Where we are

Phase 0 (foundation), in progress.

## Done

- Repository scaffold: package layout, uv and hatchling, ruff, mypy strict, pytest, pre-commit, CI for Python 3.11 and 3.12.
- Project documents, ADRs 0001 to 0014.
- `docs/sources.md`: case facts for Osino, South Railroad, Sorby Hills and White Dam verified against issuer releases; calibration sources triaged.
- Independent Decision Maker running in its own chat. Decisions so far: DR-001 (ADR 0013), DR-002 (ADR 0014).
- WP 0.4 started: priors schema, loader and tests; stage priors entered per ADR 0013.

## In progress

- WP 0.4: remaining priors (capex overrun, ramp-up, gold volatility, real risk-free curve, dilution, analyst-mode discount rates, buyer's required return).
- WP 0.3: full texts of Bertisen and Davis (2008), Suárez Nieto et al. (2024), Davis (1995) and Iddon (2015); S&P phase split.
- Producing-royalty control search under ADR 0014.

## Blocked

- Push to GitHub: the Claude GitHub app does not yet have access to this repository (owner action).
- Paywalled papers: Chrome site permission for the University of Toronto library, or the owner downloads the PDFs.
- Local `sources/` folder: folder access needs the Claude desktop app open.
- WP 0.5 case templates: need the Osino DFS and South Railroad PFS technical reports and the Osino circular (March 25, 2024).

## Next

1. Finish WP 0.4 with sourced overrun and ramp-up priors once the papers are in hand.
2. WP 0.5: input template schema; fill Osino and South Railroad from the reports.
3. Control search under ADR 0014; check Cozamin's mine plan for production by concession.
