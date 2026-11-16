# 0018. Tax under a different gold price in schedule mode

- Status: accepted
- Date: 2026-11-16
- Decided by: Mastermind (routine), with validation evidence below

## Context

Schedule mode reproduces a study's own cash-flow table. When the simulated gold price differs from the study deck, revenue, revenue-linked costs and tax change. Rebuilding each study's full fiscal model (depreciation schedules, loss pools, jurisdiction-specific taxes) from a technical report is slow and error-prone, and the reports do not always give enough detail.

## Options

1. Rebuild the full fiscal model per case.
2. Study tax plus a marginal rate times the change in pre-tax profit, floored at zero per period.
3. As option 2, with any negative tax carried forward as a credit against later tax (loss carry-forward at a constant rate).

## Decision

Option 3. The marginal rate is entered per case with its source (`study.marginal_tax_rate`). After-tax cash flow is built from the study's own after-tax line plus the changes, so the study deck reproduces the table exactly.

## Evidence

Engine NPV5 against each study's published price sensitivity:

| Case | Prices tested (US$/oz) | Pre-tax error | After-tax error |
|---|---|---|---|
| Osino Twin Hills (DFS Table 22.4.2) | 1,500 to 2,000 | n/a | +0.2% to +0.3% |
| South Railroad (PFS Table 22-6) | 1,200 to 1,600 | within 0.1% | -2.3% to +5.2% |

Option 2 gave Osino -11.4% at US$1,500 (no loss carry-forward). South Railroad's larger after-tax error comes from blending Nevada's net proceeds tax, which does not carry losses forward, with federal tax into one rate.

## Consequences

Tests hold the errors above. The South Railroad after-tax limitation is stated in `methodology.md`; it affects the project and equity claims and the build decision, not the royalty's own cash flows. Option 1 remains available per case if a later result is sensitive to it.
