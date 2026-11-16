# 0006. Commodity scope and order

- Status: accepted
- Date: 2026-11-15

## Context

Each commodity needs its own price model and calibration. Building several at once delays the first working case.

## Decision

- Phase 1: gold, modelled with geometric Brownian motion. Schwartz (1997) could not fit a one-factor mean-reverting model to gold.
- Phase 2: silver and lead, plus a simple by-product copper treatment. Needed for Sorby Hills.
- Phase 3: copper with the Schwartz-Smith (2000) two-factor model; uranium with a term price and consensus deck, flagged as a weaker price model.

## Consequences

Phase 1 cases are gold projects only (Osino Twin Hills, South Railroad). Silver credits in gold studies are carried at the study's deck until Phase 2.
