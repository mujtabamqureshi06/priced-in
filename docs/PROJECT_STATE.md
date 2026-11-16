# Project state

Updated: 2026-11-16 by the Mastermind.

## Where we are

Phase 0 exit criteria are met except the owner's walk-through. Phase 1 core is built apart from ramp-up and the waterfall. The South Railroad inversion machinery (WP 2.5, pulled forward under ADR 0009) is built and tested; no South Railroad result exists yet because the buyer's spread is not calibrated (ADR 0014).

## Done

- Repository, CI (3.11 and 3.12), ADRs 0001 to 0025. Decision Maker records DR-001 to DR-011 are ADRs 0013 to 0017, 0019 to 0021 and 0023 to 0025.
- Priors registry with status `J` for stated judgments: stage priors, capital overrun, McNulty ramp-up curves and weights, base timing per case, build hurdle and window, gold convenience yield.
- Cases: South Railroad (PFS 2020, reproduces NPV5 exactly) and Osino Twin Hills (DFS 2023, within cell rounding).
- WP 1.2 price model; WP 1.3 schedule-mode cash flow (ADR 0018).
- WP 1.1, 1.4, 1.6 and the royalty part of 1.8: `pricedin.engine.simulate` with stage gates, delay, overrun (ADR 0015), the fixed build rule, and the royalty with advance royalties as a fixed nominal C$ stream valued by covered interest parity (ADRs 0021, 0022, 0024). All risks off returns the study NPV exactly.
- Market snapshots for 2021-06-07 and 2023-07-13 with sources (ADR 0024).
- WP 2.5 inversion: closed-form odds for each added delay, shape test, zero-delay odds and certain-build delay (ADRs 0023, 0025). Synthetic recovery passes.

## Next

1. Producing-royalty controls and the spread calibration (ADR 0014); DR-012 is with the Decision Maker.
2. WP 1.5 ramp-up (ADR 0019) and WP 1.9 waterfall.
3. `docs/cases/south_railroad.md` with the ADR 0021, 0023 to 0025 disclosures, then the first South Railroad frontier.
4. Equity claim and dilution (WP 1.8 remainder).

## Open

- LBMA PM cross-check of the gold spot values (ADR 0024).
- Gold Standard guidance on a Record of Decision date published on or before 2021-06-07 (ADR 0023 sensitivity).
- Dilution prior: the Iddon (2015) offering study could not be located.
- Osino circular (March 25, 2024) for diluted shares and net cash: needed for WP 2.3 and 2.4.

## Owner

- Walk-through of the design (Phase 0 exit criterion); the design walk-through document ends with self-test questions.
- Before any publication (Tier 3, about ten minutes on a library Bloomberg terminal): COMEX gold futures for 2021-06-07 and 2023-07-13, and the longest liquid gold implied volatility, to check the zero convenience yield (ADR 0024).
