# 0051. Phase 4 panel design

- Status: accepted
- Date: 2026-11-16

## Context

Phase 4 asks whether build odds implied by developers' market values carry information about which projects reach a construction decision. The binding cost is the mine plan at each snapshot, not the price data. Survivorship is the main threat to the test.

## Decision

1. **Core panel:** ASX-listed single-project gold developers with a first PEA, PFS or FS in 2012 to 2021, drawn from a complete, dated candidate list that includes delisted companies. Inclusion is decided before documents are checked, and drops are reported by outcome. TSX and TSXV names found through company archives form a labelled supplementary set only.
2. **Mine plans:** a parametric builder calibrated to each study's after-tax NPV and IRR. It is validated on a random, hand-transcribed subsample (the larger of 10 projects or 20%), and its measured tolerance is carried into the results.
3. **Outcomes:** a construction decision within 36 months is the event; a takeover is a competing outcome; abandonment is an observed non-event. Sold projects are followed under the new owner, and only untrackable projects are censored.
4. **Protocol first:** `docs/phase4/protocol.md` is frozen, with its commit hash recorded, before any outcome data is collected. Expected power is stated in it.
5. **Blocking check:** if no share-price source covers delisted ASX companies from 2012 to 2024, the panel does not proceed.

## Consequences

- Results apply to ASX gold developers and say so.
- The issue-discount prior (#94) is re-estimated from the financings recorded during labelling.
