# Phase 7 build-trigger study: specification

Status: fixed before any trigger is computed (ADR 0076). The study is exploratory. It does not feed the design of the study-entry tool.

## Question

Each project has a trigger G*: the gold price above which the engine's build rule says "build now" on the project's entry study. When real gold stands above a project's trigger at a quarter-end, is a construction decision in the next quarter more likely? The comparison is conditional on study stage.

Moel and Tufano (2002, Review of Financial Studies 15(1)) found that the opening and closing of 285 gold mines between 1988 and 1997 broadly follow option logic. This study asks a narrower question, about construction, on a small panel. A null result is informative too.

## Panel

- **Projects.** The Phase 4 primary panel: 80 projects (ADR 0058 rule 12).
- **Quarters.** Project-quarters follow ADR 0060 rule 1. They run from the first calendar quarter-end on or after the entry study to the last quarter-end before the earliest of three dates: the construction decision, the change of control, or 36 months after the entry study.
- **Outcome.** The outcome is 1 if the construction decision falls in the following three months (ADR 0060 rule 2).
- **Reconciliation.** Rebuilt from `data/phase4/labels.csv`, the panel gives 80 projects, 838 project-quarters and 16 decisions, the same counts as the Phase 4 secondary analysis. The script stops if it does not reconcile.

## Inputs

1. **Headline figures.** These are the `pricedin.parametric.Headline` fields, taken from each project's entry study as cited in `entry_study_source` in the labels file.
   - The transcribers see no outcome columns. The outcomes were labelled publicly in Phase 4 and are known to the author.
   - A source that cannot be reached is dropped and counted. No other study is used in its place.
   - A seeded random 20% of entries is transcribed a second time, independently. If more than a quarter of the second transcriptions differ on a field, that field is re-checked for every entry.
   - The completed set is hashed before any trigger is computed, and the hash is recorded here. The transcriptions are held privately with the Phase 4 inputs.
2. **Market inputs at each quarter-end.**
   - Gold spot is the Alpha Vantage GOLD month-end close.
   - The real rate is FRED DFII10, the last observation on or before the quarter-end.
   - Volatility is the trailing 10-year World Bank monthly gold series with the averaging correction (ADR 0057).
   - The price index is US CPI for all urban consumers (FRED CPIAUCSL), for the month.

## Trigger

G* is the lowest gold price, in the study's money, at which the engine's threshold build rule (`pricedin.engine.simulate` with the build rule on) builds immediately. Both of these must hold:

- the decision NPV at the study's discount rate is at least the hurdle, which is zero;
- the decision value, net of the expected capital overrun and the expected financing dilution, is at least zero.

**Settings.** These are the same as the Phase 7 builder validation: the stage's overrun prior (the PFS prior for scoping and PEA studies), the equity financing prior, and the real rate and volatility at the entry snapshot.

**Computation.** G* is solved by bisection on US$100 to US$10,000 an ounce, to US$0.01. No simulation is used. A project with no G* in that range is dropped and counted.

## Covariate and model

- **Covariate.** The covariate is x = ln(S / G*). S is the quarter-end gold spot deflated to the study month by CPIAUCSL. G* is held fixed for each project.
- **Model.** Complementary log-log with a Firth penalty and stage as a three-level factor (PEA including scoping, PFS, FS), with a constant baseline hazard. Nothing else is added, and nothing is added after any G* is seen.
- **Inference.**
  - The primary estimate is the coefficient on x.
  - Its interval is a 95% percentile interval from a project-cluster bootstrap: 2,000 replicates, seed 20261128.
  - It is also reported as the hazard ratio for a doubling of S / G*.
- **Secondary.** The indicator S >= G* replaces x.
- **Descriptive.** The script reports quarters and decisions with gold above and below the trigger.

## Power

With 16 decisions, the usual events-based approximation for one continuous covariate (Hsieh and Lavori 2000) gives a detectable coefficient. At a 5% two-sided test with 80% power, |beta| × SD(x) must be at least 2.80 / √16 = 0.70. That is a hazard ratio of about 2.0 per standard deviation of x. Smaller associations are expected to give an interval that includes zero, and the write-up will say so.

## Sensitivities, fixed now

1. **Builder error.** Each project's calibrated cost factor is moved by the in-sample 90th-percentile builder error, minus and plus 18.9% (`docs/phase7/builder_validation.md`). G* is recomputed and the model refitted. The trigger lies where the builder is weakest, because the fresh validation tables include no project below half its capital in NPV.
2. **Phase 5 labels.** Projects whose identifier is in `data/phase5/labels.csv` take their Phase 5 construction label and date, with construction by any owner. Only the labels are used; no Phase 5 rates are used.

## Stop rule

If fewer than 60 projects have a G*, or fewer than 12 decisions remain, only the descriptive table is reported, with no model.

## What may be claimed

The study can show only an association between gold's position relative to the trigger at a quarter-end and a construction decision in the next quarter, conditional on stage. It cannot show prediction at entry, a probability, or a test of the engine's valuation. The trigger depends on a built schedule, not the study's own table. The result is reported whatever it shows.

## Order

1. This specification and `scripts/phase7_build_trigger.py`, with synthetic tests, are committed.
2. The market file is rebuilt and hashed.
3. Headline figures are transcribed blind, second transcriptions are checked, and the set is hashed. The hash is added here before the run.
4. The script runs once. It prints its commit, the run time and both input hashes before any result.
