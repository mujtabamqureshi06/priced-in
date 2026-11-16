# 0038. The least-squares Monte Carlo build decision, and which rule leads

- Status: accepted
- Date: 2026-11-16

## Context

ADR 0023 builds a project in the first year its after-tax NPV clears zero, at the study's discount rate and the path's current gold price held flat. The fixed rule ignores the value of waiting. Phase 3 adds the optimal rule by least-squares Monte Carlo (#76), using the core validated in ADR 0037.

## Decision

1. **The LSM rule** (`Risks(build_decision="lsm")`) has four parts:
   - **Decision dates:** from the build-ready year to the end of the window.
   - **Building now:** worth the market-consistent value of the project at that year, with expected prices on the market drift, study capital and after-tax cash flows, discounted at the decision rate. The decision never sees the overrun draw (ADR 0015).
   - **Waiting:** worth the regression estimate of continuing.
   - **Fitting:** the rule is fitted on independent paths, so no path's own future prices inform its decision.

   The decision rate is the valuation rate unless `lsm_rate` is set.
2. **The fixed rule stays the headline** for every published result. LSM is reported beside it as a validated comparison, described as optimal under the engine's assumptions.
3. **What is reported:**
   - **Osino:** value and mean build year at the reference spreads.
   - **South Railroad:** three rows, the fixed rule, LSM at the valuation rate, and LSM at the study's 5%.
   - **Sorby Hills:** no build decision applies, since construction has started.

## Results

`scripts/build_rule_comparison.py`.

**Osino** (December 15, 2023): at project-level real spreads of 5% or more, the two rules give the same value within Monte Carlo error and both build as soon as they can.

At zero spread and zero convenience yield, the LSM rule waits to the end of the window. Delay then lowers the present value of capital but not of revenue. This is an artefact of those two assumptions, not evidence that waiting is optimal for an operator.

**South Railroad** (June 7, 2021): zero-delay implied odds of the Vox price at the Osisko reference spreads (raw 4.3%, pre-tax 5.6%), with standard errors.

| Rule | Raw | Pre-tax | Passing paths built | Mean build year |
|---|---|---|---|---|
| Fixed, study 5% | 0.716 (0.002) | 0.797 (0.003) | 0.99 | 4.02 |
| LSM, valuation rate (-0.82%) | 0.742 (0.003) | 0.830 (0.003) | 0.93 | 4.71 |
| LSM, study 5% | 0.725 (0.002) | 0.808 (0.003) | 0.95 | 4.19 |

Most of the gap comes from the decision rate. At a common decision rate, the optimal rule defers construction on low-price paths. That is a measured value of waiting of about 1 point of implied odds.

## Limits

The value of building now uses the expected price path, so it ignores the convexity that the tax floor adds. The basis is a cubic polynomial in the gold price.

## Revisit if

At a common decision rate, the two rules differ by more than 5 points of implied odds on any case.
