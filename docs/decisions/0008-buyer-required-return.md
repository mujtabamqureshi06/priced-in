# 0008. Buyer required return is a separate, fixed parameter

- Status: accepted; amended by ADR 0014 (fallback and control criteria)
- Date: 2026-11-15

## Context

When a royalty sells for less than the engine's value of the royalty with certain, on-time construction, the gap has at least three explanations: lower build odds, later timing, or a buyer who demands a higher return than the engine's pricing implies. If the inversion solves only for odds and timing, any return premium is silently absorbed into the implied odds and overstates how pessimistic the price is.

## Options

1. Fold the required return into the implied odds.
2. Solve jointly for odds, timing and required return.
3. Calibrate the buyer's required return once, on royalty deals where development risk is absent, and hold it fixed when inverting development-stage prices.

## Decision

Option 3. The buyer's required return (or equivalent pricing spread) is a **separate parameter**. It is calibrated once on **producing-royalty controls**: disclosed royalty purchases on operating mines with published reserves and mine plans. It is then held fixed. The inversion reports odds and timing conditional on that parameter, and the sensitivity of the result to it.

## Consequences

The project needs two or three clean producing-royalty controls (see `docs/sources.md`). White Dam is not a clean control: it restarted in 2026 from historic heap-leach material with no published reserve-based mine plan. Option 2 is rejected because one price cannot identify three unknowns.
