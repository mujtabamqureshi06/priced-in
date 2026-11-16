# 0027. Replacing the futures check on the gold convenience yield (amends 0024)

- Status: accepted
- Date: 2026-11-16
- Amends: ADR 0024, condition "before publication"

## Context

ADR 0024 required a check of the zero gold convenience yield against COMEX futures from a library Bloomberg terminal before publication. That access is not available. Free sources failed: Barchart shows expired-contract history only for two years before today; Nasdaq Data Link blocks access; Yahoo Finance has no expired contracts; LBMA stopped publishing GOFO in January 2015. A front-month settlement against the vendor spot series is not usable, because the two prices are struck at different times.

## Decision

1. y stays at zero for gold, flagged, with 1% a year as a judgment sensitivity. The futures check is no longer a publication condition.
2. New publication condition: at least one gold control calibrated with the same y as the target. Every South Railroad output states that the gold convenience yield was not checked against futures prices, that the cost of delay to the royalty holder is s + y, and that gold's convenience yield is assumed similar on the control's and the target's dates.
3. One bounded attempt to find gold, copper and silver forward curves for each control and target date. If copper and silver curves cannot be found, Cozamin may be used only as a secondary control with a short-tenor proxy (such as the LME cash to 3-month spread), labelled as such, reported separately and never used alone to fix the spread; if even that cannot be sourced, Cozamin drops out.
4. If no gold control qualifies, South Railroad is reported only on a grid of s + y with no headline point, labelled illustrative.
5. Library databases are used only if their terms allow derived values in a public project; only derived figures may be committed.

## Conditions

Front-month settlements against vendor spot are not used as a proxy. No pre-2015 GOFO-based lease rate is used for 2020 to 2023 dates.

## Revisit if

A dated gold forward curve for any control or target date becomes available, or the calibrated gold control's spread is near zero.
