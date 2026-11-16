# Project state

Updated: 2026-11-16 by the Mastermind.

## Where we are

Phase 0 criteria are met apart from the owner's walk-through. Phase 1 is built and released as v0.1.0 (private); ramp-up is not modelled in the public cases (ADR 0029). Phase 2 is under way: the South Railroad royalty inversion (ADR 0028) and a provisional reading of the Osino bids (ADR 0032) are done; the undisturbed Osino value and the developer value wait for sourced inputs.

## Done

- Repository, CI (3.11 and 3.12), ADRs 0001 to 0025. Decision Maker records DR-001 to DR-011 are ADRs 0013 to 0017, 0019 to 0021 and 0023 to 0025.
- Priors registry with status `J` for stated judgments: stage priors, capital overrun, McNulty ramp-up curves and weights, base timing per case, build hurdle and window, gold convenience yield.
- Cases: South Railroad (PFS 2020, reproduces NPV5 exactly) and Osino Twin Hills (DFS 2023, within cell rounding).
- WP 1.2 price model; WP 1.3 schedule-mode cash flow (ADR 0018).
- WP 1.1, 1.4, 1.6 and the royalty part of 1.8: `pricedin.engine.simulate` with stage gates, delay, overrun (ADR 0015), the fixed build rule, and the royalty with advance royalties as a fixed nominal C$ stream valued by covered interest parity (ADRs 0021, 0022, 0024). All risks off returns the study NPV exactly.
- Market snapshots for 2021-06-07 and 2023-07-13 with sources (ADR 0024).
- WP 2.5 inversion: closed-form odds for each added delay, shape test, zero-delay odds, certain-build delay, break-even spread (ADRs 0023, 0025, 0028). Synthetic recovery passes.
- WP 1.9 waterfall (`pricedin.report`).
- Producing-royalty controls (`pricedin.controls`): Wharf (Metalla, 2020) qualifies as a Tier 2 control; Osisko's 2020 audited impairment rate is the convention reference (ADRs 0026 to 0028).
- Relationship check on control buyers and sellers: done; the owner has no relationships with any of them.

## Done overnight (2026-11-16)

- ADRs 0029 to 0032; equity claim with dilution; sensitivities and readout; Osino write-up; Streamlit app; methodology and calibration complete; README rewritten; v0.1.0 released; equity-based inversion; Osino bids across a project-level spread. See `docs/AUTONOMY_LOG.md` for actions taken in place of the owner.

## Next

1. Osino: net cash and option proceeds from Osino's own statements and the March 2024 circular; a sourced corporate G&A burn; then the undisturbed (December 15, 2023) and developer (July 2023) values (ADRs 0031, 0032).
2. A project-level spread calibrated on producing-mine transactions (ADR 0032 revisit), and a second producing-royalty control (ADR 0028).
3. Phase 2 back-test across the Vox deals (Sorby Hills, White Dam) once their cases are built.
4. Phase 3 planning: Longstaff-Schwartz build decision and the multi-asset adapter.

## Open

- LBMA PM cross-check of the gold spot values (ADR 0024); no free source found yet.
- Gold Standard guidance on a Record of Decision date published on or before 2021-06-07 (ADR 0023 sensitivity).
- Dilution prior: the Iddon (2015) offering study could not be located.
- Osino circular (March 25, 2024) for diluted shares and net cash: needed for WP 2.3 and 2.4.

## Owner

- Walk-through of the design (Phase 0 exit criterion); the design walk-through document ends with self-test questions.
- South Railroad wording approved by the owner on 2026-11-16 (ADR 0028). Library session permitted, not a blocker (ADR 0027). See `docs/AUTONOMY_LOG.md`.
- Making the repository public remains the owner's decision.
