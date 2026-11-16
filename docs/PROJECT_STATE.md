# Project state

Updated: 2026-11-16 (evening) by the Mastermind.

## Where we are

Phase 2 closed with v0.2.0 on 2026-11-16: synthetic recovery passes for every adapter, the public back-test regenerates from one command, the control deviation is explained, and the owner approved the write-up and the Sorby Hills wording. The repository is public (owner, 2026-11-16) and the app is live at https://priced-in.streamlit.app/. Phase 3 is next.

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

## Done (2026-11-16, afternoon)

- WP 2.7: `data/transactions.csv` with loader and checks; White Dam listed, not a control (ADR 0034).
- WP 2.6: `pricedin.royalty_cases` and `CorrelatedGBM` (ADR 0036). Sorby Hills royalty case on the FEED schedule (ADR 0035, DR-020); draft write-up `docs/cases/sorby_hills.md` awaiting the owner's wording review. The price equals the on-schedule value at a 2.3% real spread.

## Next

1. Phase 3 plan: Longstaff-Schwartz build decision (validated against Brennan and Schwartz 1985 and a reference implementation), multi-asset adapter, multi-metal project engine (ADR 0036), copper.
2. Osino July 2023 developer value: the circular (p. 109) gives the July 2023 range, C$1.07 to C$1.20; the Q1 2023 statements (the last balance sheet public before July 13, 2023) are still to be retrieved from the archived company website.
3. A project-level spread calibrated on producing-mine transactions (ADR 0032 revisit), and a second producing-royalty control (ADR 0028).
4. Phase 3 planning: Longstaff-Schwartz build decision, multi-asset adapter, multi-metal project engine (ADR 0036).

## Open

- LBMA PM cross-check of the gold spot values (ADR 0024); no free source found yet.
- Gold Standard guidance on a Record of Decision date published on or before 2021-06-07 (ADR 0023 sensitivity).
- Dilution prior: the Iddon (2015) offering study could not be located.
- Osino circular (March 25, 2024) for diluted shares and net cash: needed for WP 2.3 and 2.4.

## Owner

- Walk-through of the design (Phase 0 exit criterion); the design walk-through document ends with self-test questions.
- South Railroad wording approved by the owner on 2026-11-16 (ADR 0028). Library session permitted, not a blocker (ADR 0027). See `docs/AUTONOMY_LOG.md`.
- Repository made public by the owner on 2026-11-16, after the full-history confidentiality check recorded in `docs/AUTONOMY_LOG.md`.
- App deployed by the owner on Streamlit Community Cloud: https://priced-in.streamlit.app/.
- Sorby Hills wording and the back-test write-up approved by the owner on 2026-11-16.
