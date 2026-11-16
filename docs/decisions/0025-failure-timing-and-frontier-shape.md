# 0025. Failure timing under added delay, and frontier shape

- Status: accepted
- Date: 2026-11-16
- Supersedes: the failure-timing clause of ADR 0022 (item 2)

## Context

The inversion (WP 2.5) solves, for each added delay d, the gate odds q(d) at which the royalty value equals the price. Value is exactly linear in q, so q(d) = (price - V_fail(d)) / (V_pass(d) - V_fail(d)). Under ADR 0022 a failing path failed at the delayed build-ready year, so added delay also lengthened the advance royalties on paths that are never built. That mixed the two beliefs the frontier is meant to separate and could make the frontier slope down for reasons unrelated to timing.

## Decision

1. A path that fails a stage gate fails at the **base** build-ready year (`years_to_start`, ADR 0023), whatever the added delay. Advance royalties stop then (ADR 0021). V_fail is constant in d.
2. Added delay applies only to paths that pass. On those paths the build-ready year, the advances paid until production and the build window (ADR 0023) all run from the delayed build-ready year. The frontier axis is labelled "years late, for a project that is built".
3. Bias, stated wherever the frontier appears: if failing projects in fact linger and keep paying advances, this understates their value and slightly overstates implied odds.
4. Option (a), "failure discovered at the delayed date" (`Timing.failure_after_delay = True`), is a named sensitivity reported in the case write-up, not in headlines.
5. Shape test: every delay uses the same random paths. Each step is tested against two standard errors of that step (delta method on the per-path difference). Any significant fall: "not monotone", and the shape is reported instead of the bounds. No significant step: "flat within Monte Carlo error", not called monotone. Otherwise "rising".
6. Where q exceeds 1, report the delay at which it crosses 1 as the certain-build delay. Values above 1 are reported as "no solution: price above the certain-build value at this delay", never as a probability.

## Conditions

Internal South Railroad figures computed with a placeholder spread stay out of every committed document, commit message and update until the spread is calibrated under ADR 0014.

## Revisit if

- A source shows how long failed development projects keep paying advance or minimum royalties before termination.
- Under this rule, with advances not credited, the frontier slopes down at the calibrated spread.

Confidence: high.
