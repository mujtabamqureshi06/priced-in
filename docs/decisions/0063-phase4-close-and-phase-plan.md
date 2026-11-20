# ADR 0063: Phase 4 close-out and the plan for later phases

- Status: accepted
- Date: 2026-11-19

## Context

The Phase 4 test is complete (`docs/phase4/results.md`). The price-to-built-value ratio ranked later construction decisions modestly (AUC 0.624 [0.468, 0.770], 80 projects, 16 events). It did no better than P/NAV or the study stage.

The second sample fixed in ADR 0062 screened to 35 entrants and about 9 expected events. Its confirmatory threshold of 100 projects and 25 expected events cannot be reached.

The builder validation passed on the engine that produced the result. It failed the 90th-percentile threshold on the corrected engine (ADR 0059), where projects near break-even drive the misses.

## Decision

1. **Phase 4 closes when four things are done.**
   - The checks fixed in advance are all reported. Those finished at close are:
     - (a) construction at each study's own schedule;
     - (b) excluding companies with another resource-stage project;
     - (c) the check panel with tax-modelled entries;
     - (d) screen recall.
   - The write-up discloses every point a reader could use to discount the result:
     - the run timing;
     - which rules were fixed after labelling;
     - the second-coding caveat;
     - the calibration inversion;
     - the sign reversal in the lagged hazard;
     - the builder thresholds set after four errors were known.
   - Every published figure uses the corrected engine.
   - One pull request merges with CI green.
2. **Study-timing definition for check (a).** Construction starts at the study's stated first production less its stated pre-production period. Otherwise the one-year default stays, flagged. The definition was fixed after the primary result was known. It is mechanical, and the trigger of 0.03 still applied.
3. **The second sample is shelved as a test of the ratio.**
   - No predictor is computed for it, and no outcome is labelled for that purpose.
   - Its screening record is kept, private.
   - Its projects may enter the Phase 5 stage table, under that phase's own protocol, written before any of their outcomes are labelled.
4. **Builder error.**
   - Both validation results are reported, with the error also stated as a share of initial capital.
   - Any later use of the builder with the corrected engine reports error bands by project margin.
   - That use must pass the thresholds on at least ten newly transcribed tables, drawn by a recorded seed and hashed before comparison. A re-test on the twelve tables used here is labelled in-sample.
5. **Later phases.**
   - **Phase 5, stage-to-build table.** It is built on a frame that needs no prices: every gold project with a qualifying economic study in the sample-1 frame and the stock sample. The frame and its counts are recorded before any new outcome is labelled. The exit test is calibration on a time split, with pass marks fixed beforehand. Takeovers are a competing outcome. Revisit if the frame holds fewer than 120 projects.
   - **Phase 6, royalty and stream pricer.**
     - Counting comes first. A deal is usable if it has a disclosed price, is on a pre-production gold project, has a public study with economics dated before the deal, and has standard royalty or stream terms. "Usable" is defined before counting.
     - Below 25 usable deals the phase is a case series. Below 15 it merges into Phase 7.
     - Before any deal is priced, three things are fixed: the source of the spread range, a width measure, and a scoring rule that penalises width.
     - Results are published in aggregate only.
   - **Phase 7, study-entry tool.** Its first work package reduces the builder error on marginal projects. A build-trigger test runs before the tool's design is settled. It is exploratory, its specification and power are stated before the run, and the design does not depend on it.
   - **Phases 8 and 9.** Design, then launch.
   - **The ratio.** It is kept as a cross-check reported beside P/NAV.

## Consequences

- **Claims.** The project's public claim stays "what prices imply", not prediction.
- **Next phases.** They aim at outputs that can be tested against real outcomes or prices: build rates by stage, and royalty and stream prices.
- **Roadmap.** `docs/ROADMAP.md` is updated to the new phases.
