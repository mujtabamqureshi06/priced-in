# 0029. Ramp-up: DR-006 fallback for both public cases

- Status: accepted
- Date: 2026-11-16
- Decided by: Mastermind (routine), applying the fallback clause of DR-006 (ADR 0019)

## Context

ADR 0019 replaces each study's ramp-up with a McNulty (1998) curve weighted by plant class. For South Railroad it sets Year 1 stacked tonnes to the curve's Year 1 average times the steady-state stacking rate, defers the shortfall to the end of the mine life, and keeps the study's leach kinetics. Its fallback: if throughput cannot be cleanly separated from kinetics using PFS Table 22-7, report ramp-up as "not modelled" and record why.

## Why the fallback applies

1. **South Railroad.** Table 22-7 gives tonnes stacked and payable gold by year, but not the leach recovery curve that maps a year's stacking to gold recovered in later years. Deferring Year 1 tonnes therefore needs an assumed kinetic profile, which the decision forbids changing and the PFS does not tabulate by stacking year.
2. **The curve's Year 1 average.** The digitised McNulty curves start at month 6 (`data/ramp_up_mcnulty_1998.csv`). The Year 1 average needs the value at start-up, which the source does not give; any value would be an assumption.
3. **Osino.** The DFS schedule is annual and does not state the throughput ramp it assumes in Year 1, so "replace the study's ramp-up" cannot be applied without inferring it.

## Decision

Ramp-up is reported as "not modelled" in both cases, in the waterfall and in every write-up. The McNulty priors stay in the registry for use when a case provides the needed detail (a monthly ramp schedule, or a heap-leach recovery curve by stacking year).

## Consequences

The engine's values omit any ramp-up shortfall beyond what each study already assumes. For a royalty, the effect is a small timing shift in the first production years. Revisit when a case document gives the missing detail, or if a source gives the curves' start-up values.
