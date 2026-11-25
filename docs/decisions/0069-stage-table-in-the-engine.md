# ADR 0069: How the stage table enters the engine, and the implied NAV multiple

- Status: accepted
- Date: 2026-11-25

## Context

Phase 5 gives the probability of a construction decision by study stage, from what happened to gold projects with studies dated 2012 to March 2022. The engine already decides whether and when to build from the simulated gold price (ADR 0023, ADR 0038). The historical rates contain what gold did over the period. Using them directly as `Risks.stage_odds` beside a gold-driven build rule would count the gold effect twice. The stability test (protocol section 7) also found that the rates moved between the two halves of the window.

Protocol section 8 asks for the stage table to be stated as an implied NAV multiple, labelled as derived, and compared with sell-side stage multiples verified in their original sources.

## Decision

1. **The rates are not engine inputs.** They are not used as `stage_odds` or as any other parameter of a valuation.
2. **Benchmark display (study-entry tool).** The tool may show the stage rate beside the engine's figure for the same event and horizon only: the cumulative probability of a construction decision within 36 months (and 60 if shown), under the Phase 5 event definition (protocol section 5.1). If the engine cannot produce that quantity, no benchmark is shown.
   - It is shown only for projects inside the Phase 5 frame: gold, owner with no producing mine, stage PEA, PFS or FS. Otherwise the tool says there is no benchmark for this kind of project.
   - It carries its interval, its period, and two sentences: the rates moved between the 2012-2016 and 2017-2022 studies, which fall in different gold-price regimes; and on the later studies, stage rates did not forecast better than one pooled rate. The PEA rate is marked descriptive only.
   - No difference figure, no colour for above or below, and no "gap" wording. The text reads: "This is how often projects at this stage reached a construction decision. It is not a test of the price."
   - On pages about named deals it is off by default.
3. **Interim timing prior.** The default timing prior for the odds-timing frontier may be taken from the time to a construction decision in the stage table.
   - Only decisions within 48 months, the shortest follow-up in the table, enter it, for every stage.
   - Stage-specific quantiles are used only where a stage has at least 20 such decisions; otherwise one pooled distribution is used, and the count per stage is reported.
   - Quantiles carry bootstrap intervals over projects, as in the table.
   - The prior describes `Timing.added_delay`. The historical times include waiting caused by gold prices, which the build rule already models, so the prior overstates the non-gold delay after falling prices and understates it after rising ones. This is stated wherever the prior is used.
   - The frontier stays the main output. The prior marks a point on it, and the tool also shows the implied odds at its 25th and 75th percentiles.
   - The prior enters `data/priors.yaml` only once the Phase 5 results are published. It is replaced by the delay fitted in item 4 if that calibration passes.
4. **Calibration of the non-gold frictions (Phase 7).** After the builder fix and the build-trigger study (ADR 0063), the engine is run on Phase 4 panel entries along the realised monthly gold path from each study date, and fitted to the stage table on the same entries. A protocol is committed before any run. It fixes:
   - **Parameters.** At most one `stage_odds` per stage and one shared scale on a delay distribution of fixed shape, unless a parameter-recovery test on synthetic data of the same size passes first. Holding cost, overrun and financing stay at their sourced priors.
   - **Split.** Fit on studies dated 2012-2016; test on studies dated 2017 to March 2022. The targets are the stage-table incidences for the same entries and halves, defined once.
   - **Primary comparison.** On the test half, the Brier score with the realised gold path against the score with gold held flat at the study-date price, with a bootstrap interval. A lower realised-path score with an interval excluding zero reads "supported"; an interval including zero reads "not distinguishable".
   - **Pass mark against a pooled rate.** The engine's test-half Brier score is no higher than the pooled-rate forecast's, with the interval reported; if the interval includes zero, the write-up says "not detectably different".
   - **Precision.** The expected interval width at this sample size and the number of decisions per calibration cell are stated before fitting, and the work is called exploratory.
   - **Entries.** Entries built by the headline-figure builder are used only if they pass the fixed builder's thresholds, and a run on transcribed entries only is reported beside it. The write-up states that the entries come from the Phase 4 panel, whose outcomes were already seen, and how their stage mix differs from the full table. PEA values are labelled untested.
   - **Consequence.** A pass replaces the default `stage_odds` and the interim timing prior. A fail keeps the current defaults and is disclosed. The phase needs the run and the report, not a pass.
   - **Revisit.** If the reduced model cannot be identified at this sample size, or fewer than 50 entries are usable, the calibration moves to after launch.
5. **Implied NAV multiple (protocol section 8).** The stage table is stated as the multiple of study NAV that a holder would pay who values the project at its study NAV once construction is decided and at nothing before: the expected discount factor to the decision, `E[(1 + r)^-T ; T <= H]`, from the Kaplan-Meier increments of the primary table (`stage_table.discounted_incidence`). It is reported for horizons of 3, 5 and 10 years at real rates of 0%, 5% (the usual study rate) and 8%.
   - At a flat price deck, delaying construction by `k` years in the engine scales the study value by exactly `(1 + r)^-k` on every gold case in `cases/` (`scripts/phase5_implied_multiple.py`). So the closed form is the engine's result.
   - The multiple leaves out capital overrun, dilution, takeover premia and any value left in an unbuilt project after the horizon. It is labelled "derived from build rates, not observed in prices".
   - Sell-side stage multiples are compared only once read in the original document, with the publisher, date and page. They apply to the analyst's own NAV, usually on the analyst's price deck and schedule, not to the study NAV, so the comparison is of orders of magnitude, not a test.

## Consequences

- The engine keeps one source of gold-driven waiting: the build rule.
- No Phase 5 rate appears in this record, the roadmap or the protocol until the Phase 5 results are published.
- If the Phase 5 results are not published, items 2 and 3 lapse.
