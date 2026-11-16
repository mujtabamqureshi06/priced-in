# 0047. Equity value floored at zero on each path

- Status: accepted
- Date: 2026-11-16
- Amends: ADR 0030

## Context

The equity claim subtracts the value transferred to new investors from the project value. Nothing stopped it going below zero. On weak paths, or at a 90% issue discount, it did: -2,369 in one test.

## Decision

Existing holders' value is floored at zero on each path. They are not obliged to raise money at a value-destroying discount; they can sell or walk away instead, so limited liability applies. The project, royalty and stream claims on the same path are unchanged, because a buyer may still build.

Takeover prices are read against the project claim through `inversion.project_frontier`, which is not floored, because the acquirer funds construction and bears every outcome.

## Consequences

- `tests/test_engine.py` pins the floor and checks that the project and royalty values on the same paths do not change.
- Equity results rise slightly where some paths had negative equity. The undisturbed Osino and Gold Standard readings moved by more than two standard errors; the case notes say so.

## Revisit if

A case needs a negative equity payoff, for example a parent guarantee.
