# Phase 7 build-trigger study: result

Status: exploratory. The specification (`build_trigger_spec.md`, ADR 0076) and the input hashes were committed before any trigger was computed. The script ran once, on 2026-11-28 at 06:04 UTC from commit c08072a. It printed both input hashes, and they match the spec. This result does not feed the design of the study-entry tool.

## Summary

Every one of the 14 construction decisions came in a quarter when real gold stood above the project's build trigger. The primary estimate is positive, and its interval just excludes zero. But most quarters were above the trigger anyway, and two of the fixed checks have intervals that include zero, so the association is weak evidence. It is not a finding that decisions follow the trigger.

## Data

- **Panel.** The Phase 4 primary panel reconciles: 80 projects, 838 project-quarters and 16 decisions.
- **Inputs.** Headline figures were read from 74 of the 80 entry releases. 68 projects are usable; the input record in the spec lists the 12 dropped.
- **Analysed.** 709 project-quarters with 14 decisions. This is above the stop rule (60 projects, 12 decisions).
- **Calibration.** 12 of the 68 entries keep the closest schedule matching their NPV because their cash-flow shape could not be matched (ADR 0057 rule 2).

## Descriptive

| Gold at the quarter-end | Project-quarters | Decisions in the next quarter |
|---|---|---|
| At or above the trigger | 635 | 14 |
| Below the trigger | 74 | 0 |

At the entry study's own figures, most projects' triggers sit below the gold price of the time. So 90% of quarters are above the trigger, and the comparison rests on a small number of quarters below it.

## Model

Complementary log-log with a Firth penalty and stage as a factor. The intervals are 95% project-cluster bootstrap intervals (2,000 replicates).

| Reading | Projects | Decisions | Coefficient on ln(spot / G*) [95% CI] | Hazard ratio per doubling |
|---|---|---|---|---|
| Primary | 68 | 14 | +0.83 [+0.11, +2.84] | 1.78 |
| Without shape-not-matched entries | 56 | not printed | +0.42 [-0.32, +2.24] | 1.34 |
| Cost factor -18.9% | 68 | 14 | +0.91 [+0.17, +3.01] | 1.88 |
| Cost factor +18.9% | 68 | 14 | +0.77 [+0.06, +2.71] | 1.71 |
| Phase 5 labels (48 of 80 matched) | 68 | 15 | +0.66 [-0.09, +2.81] | 1.58 |

**Secondary.** With the indicator "spot at or above G*" in place of the ratio, the coefficient is +1.84 [-0.17, +2.73]. The upper bound is limited because no decision falls below the trigger.

## Reading

- **Power.** The specification stated that with 16 decisions only an association of about a hazard ratio of 2 per standard deviation could be detected. The primary interval is wide and its lower end is near zero.
- **Robustness.** Moving each project's costs by the builder's 90th-percentile error does not change the reading. Dropping the shape-flagged entries, or using the Phase 5 labels, gives intervals that include zero.
- **What this is.** At most, a weak association between gold above a project's trigger and a construction decision in the next quarter, conditional on stage. It is not a prediction, not a probability, and not a test of the engine's valuation.
- **Limits.**
  - The trigger comes from a schedule built from headline figures, not from the study's own table.
  - The trigger is held at the entry study, even where a later study changed the economics.
  - The outcomes were labelled in Phase 4 and were known before this study.
