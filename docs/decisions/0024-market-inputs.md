# 0024. Market inputs for the valuation snapshots

- Status: accepted
- Date: 2026-11-16
- Decided by: Independent Decision Maker (owner's proxy), DR-010

## Context

Market-consistent mode (ADR 0012) needs, for each valuation date, the gold spot price, a real risk-free rate, the gold convenience yield and a volatility. The raw observations are in `data/snapshots/` with source, series, date and status.

## Finding that shapes the decision

Under risk-neutral GBM the expected gold price at year t is spot × (1 + r)^t × e^(-yt). Discounting at r leaves spot × e^(-yt). So in market-consistent mode an ounce of royalty revenue t years out is worth spot × e^(-yt) whatever the real rate. The cost of delay to a royalty holder is the convenience yield y plus the buyer's spread s (ADR 0014), plus stage hazards and advance royalties. The rate r matters only through costs (the build rule), the advances, and the project and equity claims. A test holds this: with no stage risk, no advances and s = 0, the royalty value equals rate × coverage × the sum of gold revenue × spot/deck × e^(-yt), and does not change with r.

## Decision

1. **Real rate:** the 10-year TIPS yield on the date (FRED DFII10): -0.82% on 2021-06-07, 1.52% on 2023-07-13. The negative 2021 rate is kept and flagged. The full TIPS curve is a Phase 3 refinement.
2. **Convenience yield:** zero, flagged, with 1% a year as a judgment sensitivity (`market.convenience_yield.gold`). The same y is used for the target and every gold control, so the calibrated spread absorbs an error in y and s + y stays right. Where a non-gold control is used, state that the zero gold lease rate is not offset. Every South Railroad output states that the cost of delay to the royalty holder is s + y, and gives the certain-build delay at the sensitivity value as well.
3. **Volatility:** trailing 10-year realised volatility to the valuation date (14.8% for 2021, 14.1% for 2023), with GVZ on the date as a sensitivity.
4. **Spot:** the Alpha Vantage daily series, status P, cross-checked against a public LBMA PM figure for each date; a difference above 0.5% goes back to the Decision Maker. Only the single dated values are committed; the vendor series and LBMA data are stored by reference, and `scripts/realised_vol.py` rebuilds the volatility.
5. **Advance royalties (routine, ADR 0021):** the fixed nominal C$ stream is valued by discounting at the Government of Canada 10-year yield on the date (1.47%, Bank of Canada) and converting at spot USD/CAD, which is exact under covered interest parity. `engine.fixed_nominal_advance` turns this into the engine's real-terms inputs.

## Conditions

- Report y and s next to every frontier.
- Market inputs enter only through the snapshot files, never hard-coded in modules.
- **Before publication (owner, Tier 3):** pull COMEX gold futures for 2021-06-07 and 2023-07-13 from a library Bloomberg terminal, and the longest liquid gold implied volatility if available. Back out y with nominal rates. If it differs from zero by more than 0.5% a year, it becomes the headline. This does not block building.

## Revisit if

- The futures-implied y for either date differs from zero by more than 0.5% a year.
- The calibrated spread is near zero, so the cost of delay is near zero.
- The LBMA cross-check differs by more than 0.5%.
- GVZ against realised volatility moves South Railroad's zero-delay implied odds by more than 5 percentage points.

Confidence (Decision Maker): high on items 1, 3 and 4 and on the cancellation result; medium on y = 0 until the futures check. Owner review: not required, apart from the Tier 3 data pull. Study item: why waiting costs a gold royalty holder only the lease rate plus the buyer's spread under market pricing.
