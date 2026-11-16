# 0022. Engine timing conventions

- Status: accepted
- Date: 2026-11-16
- Amended by: ADR 0025 (item 2: failure now occurs at the base build-ready year)

## Context

The simulation engine (`pricedin.engine`) needs fixed conventions for when things happen on a path: when a stage gate fails, when the build rule may act, when advance royalties are paid, and how an overrun meets tax. These are modelling conventions, not calibration values. The values that need a source or a judgment (years to construction start, the delay distribution, the build-rule hurdle and window) are parameters, set in ADR 0023.

## Decision

1. Time runs in whole years from the valuation date, with end-of-year cash flows. With no delay, the study's first schedule period (its t0 column) falls `years_to_start` years after the valuation date.
2. A path draws its stage gates once, with the cumulative odds of the remaining gates. A path that fails, fails at the build-ready year (`years_to_start + added_delay`).
3. The fixed build rule (WP 1.6) tests each year from the build-ready year to the end of the window (`max_wait` years later). It builds in the first year in which the project's after-tax NPV, at that year's gold price held flat, at the study's capital estimate and discount rate, is at least the hurdle. It never sees the overrun draw (ADR 0015).
4. Advance minimum royalties are paid at the end of each year before the first production year. On a path that fails a gate they stop at the build-ready year; on a path the rule never builds they stop when the window closes (ADR 0021).
5. Extra capital from an overrun carries no tax shield. This understates value slightly on overrun paths and is stated in the methodology.
6. Ramp-up (ADR 0019) is applied in a later pull request; until then outputs say it is not modelled.

## Consequences

With all risks off, a flat study deck, the study's discount rate and no delay, the engine returns the study NPV exactly; a test holds this. Tests also check gate scaling, delay discounting, the mean effect of the overrun against its closed form, build-rule extremes, that the rule ignores the overrun, royalty and advance hand calculations, and reproducibility by seed.
