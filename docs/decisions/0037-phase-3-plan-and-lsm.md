# 0037. Phase 3 sequence and the least-squares Monte Carlo core

- Status: accepted
- Date: 2026-11-16

## Context

Phase 3 has one hard exit criterion: the Longstaff-Schwartz build decision, validated against QuantLib and against a replication of the Brennan and Schwartz (1985) copper mine. The other work packages add breadth:

- WP 3.1: multi-asset adapter.
- WP 3.3: copper.
- WP 3.4: uranium.
- WP 3.5: Shapley-value waterfall.
- WP 3.6: streams.

ADR 0036 also moved the multi-metal project engine here.

## Decision

1. **Order.**
   1. WP 3.2: the LSM core and its validation.
   2. WP 3.2: the LSM build decision in the engine, replacing the fixed rule as an option. The fixed rule stays as the reference (ADR 0023).
   3. WP 3.5: Shapley attribution. It is small, and the LSM changes the waterfall's last step.
   4. WP 3.3 with the multi-metal project engine, then the Brennan and Schwartz replication, which needs copper.
   5. WP 3.1, WP 3.6, WP 3.4.
2. **The LSM core** (`pricedin.lsm`) is generic optimal stopping, as in Longstaff and Schwartz (2001):
   - Regression only on in-the-money paths.
   - Polynomial basis in the scaled state.
   - Backward induction.
   - An optional out-of-sample valuation on fresh paths.

   Where too few paths are in the money to regress, the rule waits rather than stops.
3. **Validation dependency.** QuantLib is a `validation` dependency group, installed in CI. Tests skip if it is absent.

## Validation result

The American put in the Longstaff and Schwartz (2001) Table 1 setting:

- Inputs: S = 36, K = 40, r = 6%, volatility 20%, one year, 50 exercise dates.
- Paths: 100,000, antithetic.

| Method | Value |
|---|---|
| QuantLib finite differences (2,000 by 2,000 grid) | 4.487 |
| LSM, in sample | 4.486 |
| LSM, out of sample | 4.456 (standard error 0.009) |
| European (Black-Scholes) | 3.844 |

The out-of-sample estimate is low by about 3 cents. That is the expected bias of a suboptimal rule on fresh paths. The tests allow 5 cents below the reference and three standard errors above it. With one exercise date the method returns the Black-Scholes value within three standard errors.

## Consequences

The engine can now value build timing as an option on the gold price rather than by a fixed rule. The next step defines the build payoff and the state variables, which are a design question for the engine, not for `pricedin.lsm`.
