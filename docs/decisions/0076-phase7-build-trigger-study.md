# 0076. Phase 7 build-trigger study

Date: 2026-11-28
Status: accepted

## Context

The phase plan (ADR 0063) includes an exploratory test of whether construction decisions follow the engine's build trigger, run before the study-entry tool is designed and independent of it. The Phase 4 entry headline figures that the parametric builder used are not available in reusable form, so they must be transcribed again from the cited entry studies.

## Decision

- The specification is `docs/phase7/build_trigger_spec.md` and the script is `scripts/phase7_build_trigger.py`. Both are committed before any trigger is computed.
- The trigger is the lowest gold price at which the threshold build rule builds now, on the Phase 7 validation settings.
- The panel is the Phase 4 primary panel and quarters (ADR 0058 rule 12, ADR 0060 rules 1 and 2), and the script checks it against 80 projects, 838 quarters and 16 decisions.
- Headline figures are transcribed without outcome columns, only from the cited entry study, with a 20% second transcription. They are hashed before any trigger is computed.
- Gold spot is deflated to the study month by CPIAUCSL before the ratio is taken.
- There is one primary estimate, the coefficient on ln(spot / G*) with stage. The secondary estimate uses the indicator. Two sensitivities are fixed: the cost factor moved by ±18.9%, and Phase 5 labels.
- Stop rule: with fewer than 60 projects or 12 decisions, the study is descriptive only.

## Consequences

- With 16 decisions only a strong association is detectable (about a hazard ratio of 2 per standard deviation). An interval including zero is the expected result.
- The same transcriptions can later serve the calibration in ADR 0069.
- The result does not change the tool's design.
