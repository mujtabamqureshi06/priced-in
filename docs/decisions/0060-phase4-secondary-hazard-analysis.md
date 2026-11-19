# 0060. Phase 4 secondary analysis: discrete-time hazard on quarterly snapshots

- Status: accepted
- Date: 2026-11-19
- Amends: ADR 0055 (secondary analyses)

## Context

The primary Phase 4 test reads one snapshot per project, at entry. A secondary analysis uses every quarter-end from entry to the decision or the end of the window, so a price that moves before a decision can be related to it. This record fixes the specification before the model is run on outcomes. The quarterly ratio values were computed before this record, without outcomes, with the engine at commit b5e3eb8, and hashed: `quarterly_odds_N200000.csv`, SHA-256 035c8298d4812cb191a838509ab2abc0a2a5716a37cc65882540217703fe1f49 (886 project-quarters, 870 valued). With 16 construction decisions the data support about two covariates.

## Decision

1. **Unit.** One row per primary-panel project and quarter-end t, from the entry snapshot to the last quarter-end before the earliest of: the construction decision, the change of control, the start of an outstanding offer (ADR 0055), or 36 months after the entry study. Rows without a valued snapshot are dropped and counted.
2. **Outcome.** 1 if the project's construction decision (ADR 0055 rule 1, primary dating) falls in the quarter after t, (t, t + 3 months]; otherwise 0. The covariate is therefore lagged one quarter relative to the event.
3. **Covariates.** The natural log of the price-to-value ratio at 0% spread at t, with ratios below 0.005 set to 0.005 (13 of 870 valued rows are zero or negative, where net cash exceeds market capitalisation); and study stage at entry as a three-level factor (PEA including scoping; PFS; FS including DFS and BFS). Nothing else. The baseline hazard is constant.
4. **Model.** Complementary log-log link, fitted by maximum likelihood with a Firth (Jeffreys-prior) penalty, because events are rare.
5. **Inference.** Project-cluster bootstrap: 2,000 replicates resampling projects with all their quarters, seed 20261120, percentile 95% interval for the log-ratio coefficient. Reported: the coefficient, its interval, and the implied hazard ratio for a doubling of the ratio.
6. **Checks, stated now.** (a) Drop the two quarter-ends before each decision, so a price that reacts to news leaked ahead of an announcement cannot drive the result. (b) Exclude the rows set to the 0.005 floor. (c) High- and medium-confidence labels only. (d) The ratio at 10% spread in place of 0%.
7. **What may be claimed.** Only an association between the ratio at a quarter-end and a construction decision in the next quarter, conditional on stage. Not prediction at entry, and not a probability. The result is reported whatever it shows, beside the primary result, labelled secondary.
8. **Engine.** The analysis uses the hashed file above, computed with the engine as it stood at the freeze. Values under later engine changes are exploratory.

## Consequences

- The analysis script is committed before its first run against outcomes and writes this record's commit hash and its run time in UTC into its output.
- With about 16 events, a coefficient interval that includes zero is the expected outcome unless the association is strong; the write-up says so.

## Revisit if

The number of decisions inside the analysed quarters is below 10, in which case only the descriptive event-quarter table is reported.
