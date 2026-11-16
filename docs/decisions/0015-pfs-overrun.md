# 0015. Capital cost overrun for PFS-stage cases

- Status: accepted
- Date: 2026-11-16

## Context

Bertisen and Davis (2008) is the only verified overrun source. It compares as-built cost with bankable feasibility estimates (including contingency) for 63 financed, built projects. It says nothing about PFS estimates, and South Railroad, the anchor royalty case, is a PFS.

## Options

A. Apply the FS distribution to PFS cases, flagged. B. Widen the spread by the ratio of conventional accuracy bands. C. No PFS default; require a user assumption.

## Decision

1. **Default.** PFS and FS cases both use the Bertisen and Davis distribution in real terms: 0.914 × (0.91 + lognormal with mean 0.35 and SD 0.42). The nominal form is never used. PFS cases carry the flag: "FS-stage overrun distribution applied to a PFS estimate; likely understates PFS cost risk; no source for PFS-to-FS estimate growth."
2. **Sensitivity B, mean held fixed.** Keep the shift at 0.91 and the lognormal mean at 0.35; widen only the SD by the ratio of PFS to FS accuracy bands. Source the ratio from AACE International Recommended Practice 47R-11 if it can be verified there, otherwise the AMC figures [P]; either way label the widened SD as judgment. Report B in every PFS write-up next to the default, never as the headline.
3. **The build decision does not see the overrun draw.** Bertisen and Davis measured overruns discovered after commitment. The fixed build rule (WP 1.6) tests the project at the study's capital estimate; the overrun reaches cash flows only once construction starts. If the rule could see the draw, the model would skip high-overrun paths and overstate value. `methodology.md` states this.
4. **Scope.** The per-path draw applies to initial capital including contingency (do not remove contingency) and to expansion capital (flagged as an extension beyond the paper's sample). It does not apply to sustaining capital or closure costs.

## Consequences

South Railroad runs on a sourced default with a visible flag and a stated sensitivity. Its later capital figures (2022, 2026) are never used to calibrate or check anything (ADR 0007). Revisit if a source quantifies PFS-to-FS capital growth or the Phase 4 cohort records capital estimates by stage.
