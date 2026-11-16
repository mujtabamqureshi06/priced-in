# 0013. Stage-transition priors without a cohort source

- Status: accepted
- Date: 2026-11-15
- Decided by: Independent Decision Maker (owner's proxy), decision record DR-001

## Context

The engine needs the probability that a project advances from each study stage to a build decision. No source tracks a cohort of projects through these stages. The only stage-level figures are the Sykes and Trench (2014) copper pyramid ratios, reported in Lopatnikov and Rumyantsev (2025), Table 1. They are ratios of project counts at one point in time, not conversion rates. Practitioner figures (AMC, McKinsey) are weaker still, and aggregator figures have no traceable source.

## Options

A. Sykes and Trench ratios as central values, flagged. B. Build a cohort of about 20 gold projects before Phase 1. C. Wide uninformative ranges with no central value.

## Decision

Option A, with these limits.

1. Two stage entries only: PFS to FS 0.82; FS to build decision 0.88. Status [V] for the number as reported. Each carries the flag "cross-sectional count ratio, global copper; used as a stand-in for a conversion rate", shown wherever the number is used.
2. FS to build is one combined gate covering permitting, financing and the construction decision. No separate permit or financing probabilities and no jurisdiction or financing modifiers in the defaults. A case already permitted or financed still uses 0.88; the flag says this probably understates its odds. Cases under construction skip the gate.
3. No default for PEA or earlier stages. The engine refuses to run a PEA-stage case on defaults; a user-supplied value is labelled as a user assumption.
4. Fixed values in the simulation, not random draws. Sensitivity only: FS to build has a named alternative of 0.75 (AMC, [P]) and stress bounds of 0.50 and 0.95 labelled as judgment; PFS to FS has stress bounds of 0.50 and 0.95 labelled as judgment. Both entries appear in the tornado chart, and each case write-up states the stage-risk step at 0.88 and at 0.75.
5. The flag appears in waterfall step 5, the risked value, the readout and `calibration.md`.
6. A cohort of about 20 gold projects is the first task of Phase 4. Its result replaces these priors through a new ADR.
7. WP 2.5 adds a test: rerun the synthetic inversion with FS to build at 0.88 and at 0.75. The implied cumulative build probability must agree within Monte Carlo error. If it does not, the parameterisation returns to the Decision Maker before the South Railroad inversion is published.
8. Any public comparison of implied odds with this base rate calls the base rate a weak placeholder and never describes a price as implying odds above or below the "true" odds.

## Consequences

The forward engine has an anchored, citable stage-risk step whose weakness is visible. No unsourced stage modifiers enter the defaults. Revisit if a cohort source is found, the Phase 4 cohort is complete, the test in item 7 fails, or a PEA-stage case is needed before Phase 4.
