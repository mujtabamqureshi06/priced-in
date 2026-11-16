# 0049. Holding cost during deferral

- Status: accepted
- Date: 2026-11-16
- Follows: ADR 0046

## Context

With zero convenience yield, deferring construction raises project value (ADR 0046). In practice a deferred project also carries costs while it waits: site care, permits, camp, a minimum team. Sourced holding costs are already counted where we have them: corporate G&A in the market-value readings (ADR 0033), and advance royalties at South Railroad (ADR 0021). A generic site holding cost has no source. One bounded search for a published care-and-maintenance or holding cost for development-stage projects found none that could be cited.

## Decision

1. `Risks.holding_cost` is a real cost per year, in case money units. The project pays it at the end of each year that construction is deferred beyond the base year (`years_to_start`):
   - on built paths, until the build year;
   - on paths that pass their gates but never build, until the build window closes;
   - on paths that fail a gate, until the failure is found (the base year by default, so nothing is paid; the delayed date under `failure_after_delay`).
2. It lowers the project claim and, through it, the equity claim. The royalty and stream claims are unchanged, because the holder does not pay it.
3. The default is zero. A non-zero default needs a source.
4. The build decision does not include the holding cost. With a positive cost, the fixed and LSM rules therefore wait slightly more than an operator paying it would. This is stated as a limit.

## Consequences

- No published number changes.
- `tests/test_engine.py` checks:
  - the amount and timing on built paths;
  - the failure-date rule;
  - that the royalty does not change;
  - that a negative cost is rejected.
- Revisit if a source for development-stage holding costs is found. A user can already set the cost and label it as their own assumption.
