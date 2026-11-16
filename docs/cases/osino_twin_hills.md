# Osino Twin Hills: forward valuation

Status: Phase 1 forward result, with a provisional Phase 2 reading of the two bids (ADRs 0031, 0032).

## The project

Twin Hills is Osino Resources' open-pit gold project in Namibia. The definitive feasibility study (DFS), published July 13, 2023, gives an after-tax NPV of US$480 million at 5% and US$1,750/oz gold. Both permits were granted on November 3, 2022. The valuation date is the DFS date.

## Reconciliation

With every risk off, the study deck and the study's 5% rate, the engine reproduces the DFS cash-flow table exactly and its NPV within cell rounding (US$480.1 million against US$480 million). At other gold prices the engine's after-tax NPV is within 0.3% of the DFS sensitivity table (US$1,500 to US$2,000/oz; ADR 0018). Two internal inconsistencies in the DFS are recorded in the case file: the table places all initial capital in Year 0 where the text splits it, and the table and the summary give different IRRs.

## Inputs

| Input | Value | Source |
|---|---|---|
| Gold spot | US$1,960.61/oz | Alpha Vantage, status P (ADR 0024) |
| Real risk-free rate | 1.52% (10-year TIPS) | FRED DFII10 |
| Convenience yield | 0, flagged | ADRs 0024, 0027 |
| Volatility | 14.1% (trailing 10-year realised) | ADR 0024 |
| Base timing | 1 year to the DFS Year 0 | DFS Section 25, p. 25.16 (ADR 0023) |
| Stage odds | 0.88 (FS to build), applied unchanged to a permitted project, which probably understates its odds | Sykes and Trench (2014) via Lopatnikov and Rumyantsev (2025) (ADR 0013) |
| Capital overrun | Bertisen and Davis (2008), FS stage | ADR 0015 |
| Build rule | NPV at 5% and the current gold price at least zero, within 5 years | ADR 0023 |
| Ramp-up | Not modelled | ADR 0029 |
| Equity issue | All-equity funding at a 10.54% discount (dilution upper bound) | Carpentier and Suret (2009) (ADR 0030) |

## Waterfall (US$ million)

| Step | Value | Change | Std. error |
|---|---|---|---|
| Study NPV (as published) | 480.0 | | |
| Discounting at the valuation rate (1.52% real instead of 5%) | 636.2 | +156.2 | 0.0 |
| Market gold prices (spot US$1,960.61 with its market drift, instead of US$1,750 flat) | 1,074.6 | +438.4 | 0.0 |
| Base timing (one year later) | 1,093.3 | +18.7 | 0.0 |
| Capital cost overrun | 1,038.3 | -55.0 | 1.0 |
| Ramp-up | 1,038.3 | 0.0 | not modelled |
| Stage failure | 910.0 | -128.3 | 2.6 |
| Price uncertainty and build decision | 899.0 | -11.0 | 5.8 |

For Osino Twin Hills, the engine values the project at US$899 million against the study's US$480 million (+87%). The largest single step is market gold prices, which raise value by US$438 million.

Why the engine's value is so far above the DFS NPV: it prices gold risk at market terms but carries no extra return for any other risk the project bears, beyond the stage odds and overrun it simulates. A buyer's or investor's required return for those other risks is not in this number; the bid section below shows how much it matters.

Two steps need a word. The first two together carry most of the gap, and neither is a view: they restate the study at the market's real rate and the market's gold price on the valuation date, which is what market-consistent valuation means (ADR 0012). The base-timing step is positive because, with a zero convenience yield, waiting does not lower the value of future revenue under market prices (ADR 0024), while it does lower the present value of the costs.

## Equity claim

Existing shareholders' share of project value, after the transfer to new investors when initial capital is raised at a 10.54% discount: US$856 million with all-equity funding (the dilution upper bound), US$867 million with 30% debt and US$879 million with 60% debt (ADR 0030). Underwriting fees are not modelled.

## When the project is built

| Build timing | Share of paths |
|---|---|
| Year 1 (on the assumed schedule) | 87.6% |
| Later years, deferred by the build rule | under 0.1% each |
| Never built | 12.4% |

Nearly all the "never built" share comes from the stage gate (12% at odds of 0.88). At spot prices well above the DFS deck, the build rule almost never defers.

## What moves the answer most

| Input | Low | High | Value at low | Value at high | Swing |
|---|---|---|---|---|---|
| Stage odds | 0.75 (AMC, practitioner) | 0.95 (stress) | 760.2 | 974.5 | 214.2 |
| Convenience yield | 0% (base) | 1% | 899.0 | 752.3 | 146.7 |
| Capital overrun | off | on (base) | 947.1 | 899.0 | 48.1 |
| Base timing | 0 years | 2 years | 879.6 | 910.5 | 31.0 |
| Volatility | GVZ 12.7% | 20% | 901.8 | 880.8 | 21.0 |
| Build window | 5 years (base) | 10 years | 899.0 | 894.5 | 4.5 |
| Build-rule rate | study 5% (base) | 8.9% (CIM FS) | 899.0 | 899.2 | 0.2 |

The stage odds and the gold convenience yield dominate. Both carry flags: the stage odds come from cross-sectional copper counts (ADR 0013), and the convenience yield was not checked against futures (ADR 0027).

All figures use 20,000 paths and seed 1; `scripts/osino_case.py` regenerates them.

## What the bids imply (provisional)

Both bids are compared with the project claim, because the acquirer funds construction (ADR 0031). Project price = equity value less net cash; exploration ground is valued at zero, which overstates the project price and so the implied odds; option exercise proceeds are not yet known. Net cash is from a vendor balance sheet (Barchart, status P) until Osino's own statements are obtained (ADR 0032), so these results are provisional. Each bid includes any control premium and synergies, which overstates the odds on a standalone basis.

Without a calibrated project-level spread, the implied odds absorb the acquirer's required return, so each bid is shown against a real spread on net project cash flows (ADR 0032).

| Real spread | Dundee, Dec 18, 2023 (C$278.7M, US$208.1M) | Shanjin, Feb 23, 2024 (C$358.7M, US$265.6M) |
|---|---|---|
| 0% | 0.19 | 0.23 |
| 4% | 0.26 | 0.33 |
| 8% | 0.37 | 0.46 |
| 12% | 0.52 | 0.64 |
| 15% | 0.67 | 0.82 |
| Break-even | 19.6% | 17.3% |

Reference points (spread over the 10-year TIPS yield on each date): the DFS's own 5% real (odds about 0.25 and 0.30); the CIM survey's FS-stage gold rate of 8.9% real (0.35 and 0.42); Lopatnikov and Rumyantsev's (2025) 16% real WACC for this project (0.63 and 0.76).

With no spread, the implied odds fall slightly as delay is added, because waiting lowers the present value of costs but not of revenue when the convenience yield is zero; a positive spread on net cash flows reverses this. The odds at zero spread are a point on the curve, not "the acquirer's odds".

`scripts/osino_bids.py` regenerates these figures. The undisturbed market value before the Dundee offer, the headline under ADR 0031, waits for a sourced corporate G&A burn.

## What this is not

This is a forward value under stated assumptions, not a view on Osino's share price or on the takeover terms. The Phase 2 inversion will ask what the July 2023 market value, the Dundee bid and the Shanjin agreement imply about build odds and timing.
