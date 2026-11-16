# Project state

Updated: 2026-11-16 by the Mastermind.

## Where we are

Phase 0 (foundation) nearly complete; Phase 1 core started under ADR 0009.

## Done

- Repository on GitHub with CI on Python 3.11 and 3.12; pull requests squash-merged after both checks pass. Branch protection cannot be set from the Mastermind's session.
- ADRs 0001 to 0017. Decision Maker records DR-001 to DR-005 are ADRs 0013 to 0017.
- Priors registry with loader and tests: stage priors (ADR 0013), FS and PFS capital cost overrun and the real-terms factor (Bertisen and Davis 2008, read in full; ADR 0015).
- Case template (schedule mode) and the South Railroad case from the 2020 PFS Table 22-7. Tests reproduce the published NPV5 (US$265,045k after tax, US$331,423k pre-tax) to the dollar.
- WP 1.2 gold price model (GBM, flat study deck).
- Vox South Railroad terms checked in Vox's own filings (ADR 0016): finder's fee confirmed, royalty uncapped, advance payments before production, no specific buy-down disclosed.

## In progress

- WP 1.1 and 1.3: simulation runner and schedule-mode project cash flow, including recomputing tax when the gold price differs from the study deck.
- Remaining priors: gold volatility, real risk-free curve and convenience yield for the as-of snapshot, dilution (the Iddon 2015 offering study could not be located).
- Producing-royalty control search (ADR 0014).

## Blocked on the owner

- Osino DFS technical report (SEDAR+ download has a bot check).
- McNulty (1998) for milled-case ramp-up (ADR 0017): library first.

## Open questions

- Which price is the South Railroad "total disclosed cost" under ADR 0014: US$2.079M (cash plus finder's fee) or US$2.317M (capitalised cost)? To the Decision Maker with the next batch.
- Advance royalty credit: not disclosed; ADR 0016 requires an explicit assumption with the direction of bias before the inversion is published.
