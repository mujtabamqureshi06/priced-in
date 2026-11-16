# 0012. Discounting convention and the two valuation modes

- Status: accepted
- Date: 2026-11-15
- Decided by: owner (approved in the build plan, WP 1.7)

## Context

Davis (1995) shows that simulating cash flows and then discounting each path at a risk-adjusted rate produces a distribution of NPVs that has no clear meaning and double-counts risk. Samis, Davis, Laughton and Poulin (2006) show that cash flows with different risk (for example a royalty and the operator's equity) should not share one discount rate. Analysts, on the other hand, think in flat price decks and stage-based discount rates, and Ampofo (2017) found that poor communication and lack of trust are the main barriers to adopting option-based tools.

## Decision

Two modes, always labelled in the output.

1. **Market-consistent mode (default).** Commodity prices simulated under risk-neutral dynamics (real risk-free rate less convenience yield). Cash flows discounted at the real risk-free rate. Project-specific risks (stage failure, overrun, delay, ramp-up) weighted by real-world probabilities with no added premium, following Samis et al. (2006). Output is a single expected value with its Monte Carlo standard error. No histogram of NPVs discounted at a risk-adjusted rate is ever shown.
2. **Analyst mode.** A deterministic price deck and stage-based real discount rates from the CIM survey priors (Smith 2013, as reported in Lopatnikov and Rumyantsev 2025). Its purpose is reconciliation: it reproduces a conventional NAV so a user can see how the engine's value relates to their own model.

## Consequences

Each case report shows both values and explains the difference. The treatment of project-specific risk as diversifiable is stated in `docs/methodology.md` as an assumption, since a buyer's required return on development risk is handled separately (ADR 0008).
