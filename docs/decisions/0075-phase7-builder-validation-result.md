# ADR 0075: Phase 7 builder validation result

- Status: accepted
- Date: 2026-11-28

## Context

The Phase 4 check found large builder errors on two near-break-even projects under the corrected engine. Phase 7 required the builder to meet the Phase 4 thresholds on at least 10 fresh annual tables, drawn by a recorded seed and hashed before comparison, with a shape fix if needed.

## Decision

1. The builder's shape is not changed. On rebuilt snapshots it meets the thresholds in-sample (11 tables) without a fix, and engine 2df6022 gives the same errors as the current engine.
2. The fix commit for the fresh test is the schema change of ADR 0074, which lets the tables be held as printed.
3. On the 10 fresh tables, the builder meets all three thresholds (`docs/phase7/builder_validation.md`). The Phase 7 builder criterion is met.

## Consequences

- The study-entry tool reports builder error bands by margin and by discounting convention. The evidence for projects below 0.5 times capital is in-sample only and weak.
- Studies that discount their first column a full year are valued about 10% lower by the builder. The tool states this.
- Mid-year studies carry an expected positive error (Kone, in-sample). The fresh set did not test this.
- The Phase 4 misses remain unexplained. A dated note in `docs/phase4/results.md` says so.
