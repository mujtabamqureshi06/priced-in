# 0055. Phase 4: outcome rules, takeovers and the primary predictor

- Status: accepted; rule 6 naming amended by ADR 0061
- Date: 2026-11-17
- Amends: ADR 0051 and the Phase 4 protocol (sections 4 and 6)

## Context

Outcomes for the frozen panel were labelled from public documents after the freeze. The labelling procedure did not settle how to date a construction decision when funding and the decision fall on different dates, or how to date a takeover. The protocol also did not say how takeovers enter the primary test, or at which required return the primary predictor is computed. The primary panel has 17 construction decisions among 85 projects.

These amendments were made on 2026-11-17, before any implied odds, prices or test statistics had been computed for any panel project.

## Decision

1. **Construction decision.** The event needs a company or acquirer document stating a decision to build or that construction is under way, and committed funding: signed facilities, closed equity, or the company stating that it funds the project from cash or that it is fully funded. The event date is the later of the two. Undisclosed funding does not count. Every candidate date (approval, each funding commitment, construction start, formal announcement) is recorded, and a robustness run dates events by construction start.
2. **Takeover.** Dated when the acquirer obtained control: the effective date of a scheme or arrangement, or the first take-up that gave a bidder more than 50%. Snapshots taken while a binding takeover offer is outstanding, from its announcement until it completes or lapses, are excluded.
3. **Second coding.** All press-only and low-confidence labels are recoded blind, in addition to the random 20% sample (seed 20261120). A company document replaces press wherever one is found, and results are also reported without rows that still rest on press.
4. **Takeovers in the primary test.** A takeover with no construction decision within 36 months is a non-event; a construction decision by the new owner within the window is the event. Checks: takeovers excluded; Fine and Gray; and, as exploratory, a takeover counted as an event.
5. **Primary test.** Single predictors (implied odds, price to NAV, stage) compared by AUC with a confidence interval from a bootstrap that resamples projects, and by Brier score. Models with covariates are exploratory. This follows from the event count, not from any result.
6. **Primary predictor.** Implied odds at a real spread of 0%, used as a ranking, at market-consistent gold prices with zero convenience yield and zero added delay. Its level is never presented as odds. AUC is also reported at spreads of 5% and 10%, and for each project's break-even spread (exploratory). The rank correlation across these predictors is reported before any outcome result. The calibration plot is titled as conditional on its spread.

## Consequences

- Revisit if the second coding changes more than two primary-panel event labels, if the two dating rules move the primary AUC by more than 0.05, or if the rank correlation between the 0% and 10% predictors falls below 0.8 (the result then leads with its dependence on the spread).
- With 17 events, the smallest AUC distinguishable from 0.5 at 80% power is about 0.71 to 0.74.
