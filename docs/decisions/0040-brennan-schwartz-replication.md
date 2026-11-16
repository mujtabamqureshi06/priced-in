# 0040. Brennan and Schwartz (1985) replication by least-squares Monte Carlo

- Status: accepted
- Date: 2026-11-16

## Context

Phase 3 closes only when the least-squares Monte Carlo (LSM) method is validated against two references:

- QuantLib, done in ADR 0037;
- a replication of the Brennan and Schwartz (1985) copper mine, the standard test for real-option methods in mining.

The mine has three options: close, reopen and abandon. It is described by:

- its inventory;
- operating, closing, reopening and maintenance costs that inflate over time;
- an income tax with no loss offset;
- a property tax, which acts as an extra discount rate;
- a copper price that follows geometric Brownian motion with a 1% convenience yield.

The original article was not accessible for this check (the hosting page failed). Maier (2021), *Annals of Operations Research* 299(1), 907-937, is open access. It specifies the model in discrete time (Sect. 2.2, Table 1) and reproduces Brennan and Schwartz's finite-difference values (Table 2). Those values are recorded with status S (secondary) in `data/benchmarks/brennan_schwartz_1985.yaml`.

## Decision

1. **Module.** `pricedin.switching` values the mine by LSM.
   - Inventory is a discrete state, the number of production periods left. One regression per date covers every (open or closed, inventory) state on the same simulated prices.
   - Periods are 0.2 years over a 60-year horizon, as in Maier (2021).
   - Values are the realised cash flows under the fitted policy (Longstaff and Schwartz 2001), so the estimate is low-biased.
2. **Basis.** A piecewise-linear spline in the log price with 12 knots at quantiles. A cubic or quartic polynomial basis left a low bias of 2% to 8% at low prices, where most of the value is option value.
3. **Check on payoffs and discounting.** The fixed-output mine (operate every period until the inventory is gone) has a closed-form value: each period's income tax is a call on copper. The simulation reproduces that value within Monte Carlo error.

## Result

`scripts/brennan_schwartz.py`: 40,000 paths (antithetic), seed 1. Values in US$ millions.

| Copper price (US$/lb) | Open: published | Open: LSM (std. error) | Closed: published | Closed: LSM (std. error) |
|---|---|---|---|---|
| 0.30 | 1.25 | 1.22 (0.06) | 1.45 | 1.42 (0.06) |
| 0.40 | 4.15 | 4.09 (0.09) | 4.35 | 4.29 (0.09) |
| 0.50 | 7.95 | 7.91 (0.11) | 8.11 | 8.06 (0.11) |
| 0.60 | 12.52 | 12.47 (0.12) | 12.49 | 12.45 (0.13) |
| 0.70 | 17.56 | 17.51 (0.14) | 17.38 | 17.32 (0.15) |
| 0.80 | 22.88 | 22.81 (0.16) | 22.68 | 22.61 (0.16) |
| 0.90 | 28.38 | 28.32 (0.18) | 28.18 | 28.12 (0.18) |
| 1.00 | 34.01 | 33.98 (0.20) | 33.81 | 33.78 (0.20) |

Every estimate is within one standard error of the published value. Every estimate is also below it, by 0.1% to 2.4%. That is the expected low bias of a fitted policy, and it is largest at low prices, where most of the value is option value.

The structure also matches. At US$0.30 and US$0.40 the open mine closes at once, so its value is the closed value less the US$0.2M closing cost, as in the published table.

## Consequences

The LSM machinery is validated on a mining problem with switching options, inventory and taxes, not only on a financial option. Together with ADR 0037, this meets the Phase 3 validation criterion.

The comparison should be repeated against the original article's table once it is accessible. The status of the benchmark values stays S until then.
