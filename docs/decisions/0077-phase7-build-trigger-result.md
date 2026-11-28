# 0077. Phase 7 build-trigger study result

Date: 2026-11-28
Status: accepted

## Context

The build-trigger study (ADR 0076) ran once on locked inputs: 68 projects, 709 project-quarters and 14 decisions.

## Decision

The result is recorded in `docs/phase7/build_trigger_result.md` as exploratory.

- **Primary estimate.** The coefficient on ln(spot / trigger) is +0.83 [+0.11, +2.84], a hazard ratio of 1.78 per doubling.
- **Two fixed checks include zero.** These are the estimate without the shape-flagged entries and the estimate on Phase 5 labels.
- **Descriptive.** All 14 decisions fell in quarters with gold above the trigger, against 635 of 709 quarters overall.

The reading is a weak association. No change to the engine, the builder or the study-entry tool follows from it (ADR 0063).

## Consequences

- The transcribed headline figures are kept privately with their hashes. They can serve the Phase 7 calibration (ADR 0069).
