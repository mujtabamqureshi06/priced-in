# 0032. Presenting the Osino bids

- Status: accepted; the conversion of reference rates to spreads (k - r) is superseded by ADR 0045
- Date: 2026-11-16

## Context

Against the market-consistent project claim, the Dundee and Shanjin bids imply zero-delay odds of about 0.19 and 0.23, and the frontiers slope down. With a zero convenience yield and no spread, waiting lowers the present value of costs but not of revenue. Without a calibrated project-level spread, the odds absorb the acquirer's required return, and an acquirer planning to build is not credibly pricing 0.2 odds.

## Decision

The same structure as ADR 0028, for every Osino price (developer, undisturbed and bids):

1. For each price, zero-delay implied odds against a real spread on net project cash flows, with the break-even spread at which the price equals the certain, on-schedule value.
2. Reference points, each labelled with its basis: the DFS's own 5%; the CIM survey FS-stage gold rate of 8.9% real (approximate, since it applies to deck cash flows); Lopatnikov and Rumyantsev's (2025) 16% real WACC for this project at June 2023 (p. 314); the analyst-mode cross-check.
3. The down-sloping frontier at s = 0 is explained in one plain sentence; a positive spread on net cash flows reverses it.
4. The odds at s = 0 are never published as "the acquirer's odds"; they appear only as a point on the curve.

## Conditions

- Net cash comes from Osino's own interim statements on SEDAR+, and option exercise proceeds from the March 2024 circular. Until they are obtained, the vendor balance sheet (Barchart, status P) is used and the result is labelled provisional.
- The forward write-up explains that the market-consistent project value is well above the DFS NPV because it carries no return for risks other than gold price.

## Revisit if

A calibrated project-level spread becomes available, for example from producing-mine transactions.
