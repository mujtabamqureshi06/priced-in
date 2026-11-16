# 0023. Timing inputs: base timing, reported point and build rule

- Status: accepted
- Date: 2026-11-16
- Decided by: Independent Decision Maker (owner's proxy), DR-009

## Context

The engine (ADR 0022) needs, for each case, the years from the valuation date to the study's first schedule period, a stated timing prior for any single reported point, and the build rule's hurdle and window. None of these has a single fixed source.

## Decision

**Timing rule.** For each step, use an independent sourced duration where one exists; otherwise use the company's guidance as published on or before the valuation date. Permitting time is outside the company's control and has an independent dataset; funding, FEED and construction do not.

1. **South Railroad: 4 years** to Year -1 (sensitivities 3 and 5). Basis: BLM median of 3.79 years from Notice of Intent to Record of Decision (CEQ 2020, Figure 6, p. 13), rounded. Time before the Notice of Intent and from the Record of Decision to construction are set to zero; the FS runs alongside the EIS. Label: "on-schedule permitting assumption". Flag: CEQ covers all EIS types, not mines. A guided Record of Decision date published by Gold Standard on or before 2021-06-07, if one exists, is a further sensitivity and does not replace the CEQ figure.
2. **Osino: 1 year** to Year 0 (sensitivities 0 and 2). Basis: DFS Section 25, p. 25.16 (funding by January 2024, FEED of four to five months, first gold within 24 months), permits already granted. Each Osino price takes its base timing from the information available on that price's own date.
3. **Reported point: no timing prior.** Report two numbers: the zero-delay point, stated as "the lowest build odds consistent with the price, if the project keeps to the schedule assumed at the valuation date"; and the certain-build end, "the price is consistent with certain construction only with a delay of at least X years". Check the frontier is monotone first; if it is not, report its shape instead. A judgment prior on delay is rejected.
4. **Build rule.** Hurdle: after-tax NPV of at least zero at the study's own discount rate, the path's real gold price held flat, study capital (never the overrun draw), with the study's tax and royalty burden. Sensitivity: the CIM FS-stage gold real rate of 8.9% (Smith 2013, via Lopatnikov and Rumyantsev 2025) as the decision rate. Window: 5 years after the build-ready year, 10 as a sensitivity, both judgment. Outputs show how often the window binds and the share of royalty value from advance royalties paid during deferral. Price-driven deferral is part of the engine's own timing; the frontier's added delay sits on top of it.

## Plan change

The build plan's timing prior "calibrated to S&P/MinEx lead times" is replaced: no source measures delay against a company's own schedule. Guided-versus-actual construction dates are added to the Phase 4 cohort task (ADR 0013) so a delay prior can be calibrated later.

## Conditions

- Base timing covers the full time to build-ready. Stage gates carry probability only and add no duration (the engine draws no stage durations; ADR 0022).
- Outcome dates after a valuation date (South Railroad's Notice of Intent in August 2025 and Record of Decision; Osino's closing) are used only for outcome tracking, and the case write-up says so.
- Public text never calls the zero-delay point "the market's odds".

## Revisit if

- A Gold Standard guidance date published before the valuation date differs from 4 years by 2 or more years.
- The frontier is not monotone.
- Moving the window from 5 to 10 years shifts South Railroad's zero-delay implied odds by more than 5 percentage points, or more than about 10% of paths reach the end of the window. Either makes the window a headline assumption.
- The Phase 4 cohort yields guided-versus-actual delays.

## Recorded in

`data/priors.yaml`: `timing.years_to_start.south_railroad`, `timing.years_to_start.osino_twin_hills`, `build.hurdle`, `build.window_years`. Status `J` added to the registry for stated judgments.

Confidence (Decision Maker): high on items 2 and 3; medium on items 1 and 4. Owner review: not required. Study item: the two numbers in item 3.
