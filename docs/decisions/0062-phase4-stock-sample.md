# 0062. Phase 4 second sample: every qualifying gold developer at one date

- Status: accepted
- Date: 2026-11-19
- Amends: ADR 0051 (a second, independent sample); uses ADRs 0053 to 0059

## Context

The first sample (80 developers, 16 construction decisions) could reliably detect only an AUC of about 0.73, and its result is inconclusive. A sample of fresh entries from 2022 to 2023 would hold about 15 to 20 projects, too few to detect anything below an AUC of about 0.90. Entry dates spread over 2012 to 2021 also move every value with the real rate of the day (methodology section 7). A stock sample read on one date gives more projects and one gold price, real rate and volatility for all.

## Decision

1. **Snapshot.** One snapshot: 31 March 2022. Every judgment about entry uses only documents dated on or before that day.
2. **Universe.** Every gold development project whose owner was listed on the ASX, the TSX or the TSXV on the snapshot date and that passes the protocol's exclusions (protocol section 2) judged at the snapshot: one project at study stage, not producing, at least 50% held, by-product revenue at most 20% of study revenue, not a royalty or streaming company. A cross-listed owner counts if one of its listings is on these exchanges.
3. **Entry study.** The owner's latest qualifying study (protocol section 2 and its sixteen written interpretations) published from 1 April 2017 to 31 March 2022. Earlier qualifying studies are recorded as covariates. A project whose construction was decided before the snapshot is excluded (ADR 0058 rule 1); one with a takeover offer outstanding at the snapshot is kept and flagged (ADR 0058 rule 9).
4. **Candidate sources.** (a) A Capital IQ Pro key-developments screen: primary industry gold, developments dated 1 April 2017 to 31 March 2022, headline containing "study", "feasibility", "economic assessment", "PEA", "scoping", "NPV", "PFS", "DFS" or "BFS" (run 2026-11-19, 757 developments, 254 companies). (b) The same screen for January to March 2022 from the earlier 2022 to 2023 run. (c) The first sample's candidate list. (d) Australian Government major-projects editions published on or before 31 March 2022 only. Each candidate records how it was found. Raw vendor data stays private.
5. **Event.** A construction decision (ADR 0055 rules 1 and 4) dated after 31 March 2022 and on or before 31 March 2025. Takeovers are non-events, with the checks of ADR 0055.
6. **Primary set.** The stock sample without any first-sample panel project whose first-sample outcome window ends after 31 March 2022, because the public labels file already records what happened after the snapshot for those. Stated checks: all projects; and without every first-sample panel project.
7. **When it is confirmatory.** Only if, counted from the screen before any outcome is labelled, the primary set holds at least 100 projects and at least 25 expected events, the expected count being the number of projects at each stage times the first sample's rates (PEA and scoping 10%, PFS 31%, FS 50%). Otherwise every result is descriptive. Both counts and the detectable AUC are recorded before labelling.
8. **Predictor.** The price-to-built-value ratio at 0% spread (ADR 0061), valued with the engine at commit 2df6022 (ADR 0059) and the market inputs of 31 March 2022.
9. **Market value (numerator).** Capital IQ market capitalisation plus net debt at the last report before the snapshot, plus cash raised since that report, less trailing twelve-month cash burn (the negative of operating plus investing cash flow, floored at zero) times the days since the report over 365; plus the present value of trailing twelve-month corporate G&A from the snapshot to first production, at the real rate. Capital IQ fields, confirmed in the plug-in before the pull: cash and short-term investments, total debt, cash from operations, cash from investing, general and administrative expense, period end date. The burn estimate is validated by projecting it to the next report date (median absolute error under 20%) before the predictor file is hashed; if it fails, the burn term leaves the primary and both numerators are reported. G&A over the whole mine life is a stated check.
10. **Statistics.** Primary: AUC on pairs within the same study stage (PEA including scoping, PFS, FS including DFS and BFS), pooled over strata, with a project bootstrap resampled within strata (10,000 replicates, seed recorded before the run). Secondary, two-sided: unstratified AUC, P/NAV, initial capital over market value, study IRR, and the stratified difference between the ratio and P/NAV. Before any outcome, the within-stage rank correlation of the ratio with P/NAV is reported; above 0.95 the two are declared indistinguishable in advance. Results are also reported on high- and medium-confidence labels only. Pooling with the first sample is descriptive only.
11. **Builder.** Study cash-flow tables are transcribed wherever one is published; the parametric builder is used elsewhere and flagged, with a check on transcribed entries only. Whether to normalise construction-capital timing is decided in a separate record before the predictor file is hashed.
12. **Evidence chain.** The predictor file's SHA-256 is committed before labelling starts. Labelling is done without access to predictor values. The comparison script is committed before its first run and writes this repository's commit and its run time in UTC into its output. The test is described as "rules fixed before outcomes were labelled".

## Consequences

- Inclusion, study inputs and prices are gathered outcome-blind: research notes record nothing dated after 31 March 2022.
- If the counts in rule 7 are not met, the sample is still collected and reported descriptively.

## Revisit if

A rule here cannot be applied from documents dated on or before the snapshot; record the problem and the fix before any outcome is labelled.
