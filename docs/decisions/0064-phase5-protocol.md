# ADR 0064: Phase 5 protocol, the stage-to-build table

- Status: accepted
- Date: 2026-11-20

## Context

Phase 4 showed that study stage carries most of what the market price of a developer says about a later construction decision (`docs/phase4/results.md`). Analysts apply stage risk weights by judgement. No public, outcome-calibrated table of build rates by study stage was found for gold (ADR 0063). A table by stage needs stages, dates and outcomes, not prices, so it can use a larger frame than the price test.

## Decision

Phase 5 follows `docs/phase5/protocol.md`, fixed before the frame is counted and before any new outcome is labelled. In outline:

1. **Frame.** The frame is the Phase 4 candidate list plus the stock-sample screen, without the price-test exclusions.
   - Only projects held by companies with no producing mine at the study date are included.
   - Before counting, the frame's recall is measured against an independent list of gold economic studies, and studies the frame missed are added.
   - If the frame is below 120 projects, it is extended to 2008-2011. If it is still below 120, the table is reported as descriptive.
2. **Entries.** Each project opens one entry per stage, at its first study of that stage.
   - An entry runs to the first construction decision by any owner, or to the data cut-off of 31 March 2026.
   - Takeovers and progression to the next stage are reported as separate outcomes.
3. **Deliverable.** The full-period table with intervals from a bootstrap over projects.
4. **Stability test.** The test compares 2012-2016 against 2017-2021, with three results fixed in advance:
   - whether stage beats a pooled rate on the Brier score;
   - whether stage order holds;
   - for each stage, a reading of "consistent", "different" or "too imprecise to judge".

   Passing the test is not required; the exit is that it is run and reported in the fixed wording.
5. **Second coding.** Second coding of new labels is done with no access to the repository.

## Consequences

- **Use of the result.** The table gives analysts and royalty buyers an outcome-based reference for stage risk, with its uncertainty stated. It does not price any single project.
- **Feed into later phases.** Its stage rates feed the study-entry tool (Phase 7). They are shown beside P/NAV and the price-to-built-value ratio, not in place of them.
