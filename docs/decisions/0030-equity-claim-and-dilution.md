# 0030. Equity claim and dilution

- Status: accepted
- Date: 2026-11-16
- Decided by: Independent Decision Maker (owner's proxy), DR-016; design by the Mastermind

## Decision

1. **Design.** Debt is raised at fair value and transfers no value. The equity-funded part of initial capital E (actual capital including any overrun, less the debt share of the study estimate) is raised at a discount d to fair value, transferring E x d / (1 - d) to the new investors, valued at the date the money is raised. Existing holders' value = operator share x (project value - PV of the transfer), on built paths (`engine.Financing`).
2. **Discount d:** Carpentier and Suret (2009), CIRANO 2009s-12, Table 6, p. 31: mean 10.54% (headline; the engine reports expected values, so the mean is the consistent statistic), median 9.09% (sensitivity), and 15% as a judgment sensitivity. Label: "Canadian small-company private placements, 1993 to 2003, not mining-specific."
3. **Debt share:** grid of 0%, 30% and 60%; 0% is the headline, labelled "dilution upper bound (all-equity funding)"; 30% and 60% are judgment.

## Conditions

- State the bias wherever the equity claim feeds an inversion: an upper bound on dilution understates equity value and pushes developer-adapter implied odds higher.
- Underwriting fees are not modelled; this understates dilution.
- Read Iddon (2015) in full before Phase 2's developer adapter is published.

## Revisit if

Iddon (2015) or another source gives mining-specific discounts, or a pre-deal Osino disclosure states a debt or equity plan.
