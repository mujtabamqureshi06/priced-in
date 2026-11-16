# 0009. Sequencing: a thin end-to-end slice first

- Status: accepted
- Date: 2026-11-15

## Context

The full roadmap runs to seven phases. A working, defensible result is needed early. The contribution of the project is the comparison layer, not the forward simulator, so a release with only the forward engine shows little that is new.

## Decision

Build in this order before any app polish:

1. Phase 0 foundation.
2. The Phase 1 core (simulation, gold price, cash flow, stage gates, overrun, ramp-up, fixed build rule, discounting, claims, waterfall) on Osino Twin Hills and South Railroad.
3. One royalty inversion, on South Railroad, pulled forward from Phase 2.

The app (#65) and other Phase 2 adapters follow. Any public description claims only what exists at the time.

## Consequences

#67, 2.2 and 2.5 are partly pulled forward into Phase 1 for South Railroad only. The synthetic-recovery test for the inversion (#71) is still required before the South Railroad result is shown to anyone.
