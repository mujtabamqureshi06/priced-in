# Phase 7 builder validation

Recorded 2026-11-28. The study builder (`pricedin.parametric`) rebuilds a project's annual schedule from its headline figures. This page reports how close the engine's value if built, computed from the built schedule, comes to the value computed from the study's own annual cash-flow table.

## Method

- **Value if built.** At 0% spread, construction one year after the snapshot with no wait, the build rule on (the option not to build), the stage capital overrun prior (the PFS prior for PEA studies), and equity financing dilution from the registry. 20,000 paths, seed 1.
- **Snapshots.** The first calendar quarter end after each study:
  - gold spot: the Alpha Vantage month-end close;
  - real rate: FRED DFII10 on or before the quarter end;
  - volatility: the trailing 10-year World Bank Pink Sheet monthly gold series with the averaging correction (ADR 0057).
- **Builder inputs.** Each builder input is read from the study table: construction years, life, average payable gold and initial capital. The cost factor and tilt are calibrated to the study's after-tax NPV and IRR.
- **Thresholds.** Median absolute error at most 10%, 90th percentile at most 25%, and Spearman correlation at least 0.95. These are unchanged from the Phase 4 check.
- **Conventions.** Tables are held with the conventions of ADR 0074. A C$ table is compared at the same scale on both sides, so the percentage errors do not depend on the exchange rate.
- **Comparison with Phase 4.** These settings may differ from the Phase 4 comparison, whose script was lost.

## In-sample re-test

Eleven tables: seven Phase 4 re-transcriptions, Kone (loadable once ADR 0074 was in place), and three tables whose builder errors were seen before the fresh test. Four Phase 4 tables could not be re-transcribed (Mexican Hat, Aurora, Blackwater, Golden Meadows), so this set differs from the Phase 4 twelve.

Median absolute error 8.5%, 90th percentile 18.9%, Spearman 0.973. Livengood's +31.3% is 0.01 times its capital. Kone's +18.9% reflects its mid-year discounting, which the builder does not model.

No change to the builder's shape was made.

## Fresh test

Ten tables, drawn and screened under rules hashed before any table was opened. The tables were hashed before any builder run (`docs/phase7/fresh_tables.md`, with a second hash set for seven tables re-expressed with the ADR 0074 fields only).

| Stage | NPV / capital | Error | Error as a multiple of capital |
|---|---|---|---|
| FS | 2.35 | -4.5% | -0.15 |
| FS | 1.12 | +0.8% | +0.01 |
| PEA | 8.9 | -1.7% | -0.19 |
| PEA | 1.60 | -10.7% | -0.38 |
| PEA | 0.65 | -2.4% | -0.03 |
| PFS | 0.94 | -2.7% | -0.03 |
| PEA | 1.33 | +0.4% | +0.01 |
| PFS | 1.05 | -3.6% | -0.06 |
| PEA | 1.69 | -6.8% | -0.24 |
| PEA | 1.20 | -10.7% | -0.33 |

Median absolute error 3.2%, 90th percentile 10.7%, Spearman 0.976. All three thresholds are met.

- **By discounting convention.** The median error is 2.4% where the study discounts its first column at exponent 0 (3 tables), 3.1% at 0.5 (4 tables), and 10.7% at 1 (3 tables). The builder places capital at its own valuation date, so it values these last studies lower.
- **By margin.** The median error is 2.6% for NPV between 0.5 and 1.5 times capital (6 tables) and 5.6% above that (4 tables).
- **Gaps in coverage.** No fresh table is below 0.5 times capital, so the test adds no evidence on marginal projects, where the in-sample errors are largest. No fresh table uses mid-year discounting.
