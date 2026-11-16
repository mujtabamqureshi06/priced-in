# Project state

Updated: 2026-11-16 by the Mastermind.

## Where we are

Phase 0 exit criteria are met except the owner's walk-through. Phase 1 core is built apart from ramp-up and the equity claim; the waterfall is built. The South Railroad inversion (ADR 0009 slice) has a draft result in `docs/cases/south_railroad.md`, presented across the buyer's spread because only one producing-royalty control qualifies (ADR 0028). It is not published; the owner reviews the wording first.

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

## Next

1. Houndé as a second control: Endeavour's technical report on SEDAR+ for a by-deposit schedule (ADR 0028).
2. Impairment-test rates of Franco-Nevada, Sandstorm and Royal Gold for the year before each deal date.
3. Verify the South Railroad resource figures against the 2020 PFS for the case wording.
4. WP 1.5 ramp-up (ADR 0019), equity claim and dilution (WP 1.8), Osino case write-up.

## Open

- LBMA PM cross-check of the gold spot values (ADR 0024); no free source found yet.
- Gold Standard guidance on a Record of Decision date published on or before 2021-06-07 (ADR 0023 sensitivity).
- Dilution prior: the Iddon (2015) offering study could not be located.
- Osino circular (March 25, 2024) for diluted shares and net cash: needed for WP 2.3 and 2.4.

## Owner

- Walk-through of the design (Phase 0 exit criterion); the design walk-through document ends with self-test questions.
- Approve the South Railroad wording (section "Reading the result" in `docs/cases/south_railroad.md`) before anything is published (ADR 0028).
- Optional: whether the Mastermind may use the University of Toronto library session for data searches, and whether the database terms allow derived values in a public project (ADR 0027). The Bloomberg check is replaced (ADR 0027).
