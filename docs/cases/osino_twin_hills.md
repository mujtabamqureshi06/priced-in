# Osino Twin Hills: forward valuation

Status: Phase 1 forward result, with the Phase 2 reading of the December 2023 market value and the two bids (ADRs 0031 to 0033).

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
| Capital cost overrun | 1,038.5 | -54.8 | 0.3 |
| Ramp-up | 1,038.5 | 0.0 | not modelled |
| Stage failure | 914.2 | -124.2 | 0.8 |
| Price uncertainty and build decision | 908.2 | -6.1 | 1.8 |

For Osino Twin Hills, the engine values the project at US$908 million (standard error 1.8) against the study's US$480 million (+89%). Across seeds 1 to 5 the value runs from 908.2 to 910.7, within two standard errors of each other. The largest single step is market gold prices, which raise value by US$438 million. The last step, price uncertainty and the build decision, is small: -6.1 with a standard error of 1.8.

Why the engine's value is so far above the DFS NPV: it prices gold risk at market terms but carries no extra return for any other risk the project bears, beyond the stage odds and overrun it simulates. A buyer's or investor's required return for those other risks is not in this number; the bid section below shows how much it matters.

Two steps need a word. The first two together carry most of the gap, and neither is a view: they restate the study at the market's real rate and the market's gold price on the valuation date, which is what market-consistent valuation means (ADR 0012). The base-timing step is positive because, with a zero convenience yield, waiting does not lower the value of future revenue under market prices (ADR 0024), while it does lower the present value of the costs.

### Order-independent risk steps

In a sequential waterfall, each risk's step depends on which risks were switched on before it. The Shapley version (ADR 0039) gives each risk its average marginal effect over every order. The four risk steps then read:

| Risk step | Sequential | Shapley (std. error) |
|---|---|---|
| Base timing | +18.7 | +16.6 (1.1) |
| Capital cost overrun | -54.8 | -52.0 (0.3) |
| Stage failure | -124.2 | -125.6 (0.8) |
| Price uncertainty and build decision | -6.1 | -5.5 (1.1) |

The ranking does not change. Stage failure is the largest risk step under either method.

## Equity claim

Existing shareholders' share of project value, after the transfer to new investors when initial capital is raised at a 10.54% discount: US$881 million with all-equity funding (the dilution upper bound), US$891 million with 30% debt and US$902 million with 60% debt (ADR 0030). Existing holders' value is floored at zero on each path (ADR 0047). Underwriting fees are not modelled.

## When the project is built

| Build timing | Share of paths |
|---|---|
| Year 1 (on the assumed schedule) | 88.0% |
| Later years, deferred by the build rule | under 0.1% each |
| Never built | 12.0% |

Nearly all the "never built" share comes from the stage gate (12% at odds of 0.88). At spot prices well above the DFS deck, the build rule almost never defers.

## What moves the answer most

| Input | Low | High | Value at low | Value at high | Swing |
|---|---|---|---|---|---|
| Stage odds | 0.75 (AMC, practitioner) | 0.95 (stress) | 772.4 | 980.4 | 208.0 |
| Convenience yield | 0% (base) | 1% | 908.2 | 760.5 | 147.7 |
| Capital overrun | off | on (base) | 956.4 | 908.2 | 48.3 |
| Base timing | 0 years | 2 years | 893.4 | 925.7 | 32.2 |
| Volatility | GVZ 12.7% | 20% | 910.3 | 892.7 | 17.6 |
| Build window | 5 years (base) | 10 years | 908.2 | 905.5 | 2.7 |
| Build-rule rate | study 5% (base) | 8.9% (CIM FS) | 908.2 | 908.2 | 0.1 |

The stage odds and the gold convenience yield dominate. Both carry flags: the stage odds come from cross-sectional copper counts (ADR 0013), and the convenience yield was not checked against futures (ADR 0027).

**Delay (ADR 0046).** With every gate passed, one year of delay raises project value by US$23.6 million at zero convenience yield and no spread, because expected gold grows at the real rate while costs are fixed. Delay stops adding value at a convenience yield of 1.07% (no spread), or at a real spread of 2.54% (zero convenience yield).

All figures use 200,000 paths and seed 1; `scripts/osino_case.py` regenerates them.

## What the prices imply

Each price uses the last Osino statements published before its date (ADRs 0031, 0033 and 0048). Exploration ground is valued at zero, which overstates the project price and so the implied odds (ADR 0031). Options and warrants count series by series by the treasury method, and restricted and deferred share units always count.

- **March 31, 2023 (for July 2023):** net cash of C$2.3 million. That is cash of C$8.82 million against the Nebari facility of C$5.98 million, C$0.29 million of accrued interest, and C$0.24 million of leases and other financial liabilities. Shares 158.2 million; 10.71 million options at C$0.94; warrants at C$0.88, C$1.10, C$1.35 and C$1.45; 2.68 million RSUs. The second Nebari tranche, drawn in May 2023, leaves net debt unchanged apart from its fee.
- **September 30, 2023 (for the later prices):** net debt of C$14.09 million. That is cash of C$8.34 million against the Nebari facility of C$19.68 million and C$2.75 million of leases and other financial liabilities. Shares 159.5 million; 9.43 million options at C$1.02; warrants at C$0.88, C$1.35, C$1.46 and C$1.53; 3.02 million RSUs and DSUs.

The prices:

- **Market value at the DFS, July 2023:** the July 2023 trading range, C$1.07 to C$1.20 per share (circular, p. 109). That gives C$171.7 to C$194.3 million (US$130.8 to US$148.0 million) for the equity claim with dilution (ADR 0030). Corporate G&A of C$6.9 million a year (Q1 2023, annualised) is deducted over the mine life.
- **Undisturbed market value, December 15, 2023:** C$1.132 per share, implied by DPM's stated 37.2% premium to that day's close. That gives C$199.6 million (US$149.3 million) for the same claim, with G&A of C$7.3 million a year (nine months to September, annualised; ADR 0033).
- **Dundee Precious Metals offer, December 18, 2023:** C$287 million. After net debt and exercise proceeds, that is C$279.6 million (US$208.8 million) for the project claim. It includes any control premium and synergies, so it overstates the odds on a standalone basis.
- **Shanjin offer, February 23, 2024:** C$368 million, or C$360.6 million (US$267.1 million) for the project claim. Same caveat.

Without a calibrated project-level spread, the implied odds absorb the required return. Each price is therefore shown against a real spread on net project cash flows, in market-consistent mode (ADR 0032). Standard errors are under 0.002 throughout.

| Real spread | July 2023, C$1.07 to C$1.20 | Undisturbed, Dec 15 | Dundee, Dec 18 | Shanjin, Feb 23 |
|---|---|---|---|---|
| 0% | 0.15 to 0.16 | 0.15 | 0.19 | 0.23 |
| 4% | 0.22 to 0.25 | 0.23 | 0.26 | 0.33 |
| 8% | 0.33 to 0.37 | 0.34 | 0.37 | 0.46 |
| 12% | 0.50 to 0.56 | 0.50 | 0.52 | 0.64 |
| 15% | 0.70 to 0.79 | 0.70 | 0.66 | 0.82 |
| Break-even | 17.0% to 17.9% | 18.1% | 19.7% | 17.3% |

Reference rates are read the way their sources used them, with this engine's stage and overrun risks on top (ADR 0045). Gold is flat in real terms at the source's deck, or at spot where none is stated, and discounted at the stated rate.

| Reference | Gold | July 2023 | Undisturbed, Dec 15 | Dundee, Dec 18 | Shanjin, Feb 23 |
|---|---|---|---|---|---|
| DFS, 5% | US$1,750 (DFS deck) | 0.43 to 0.49 | 0.50 | 0.52 | 0.66 |
| Eight Capital fairness opinion, 10.5% | US$1,850 (its deck) | 0.62 to 0.70 | 0.71 | 0.72 | 0.92 |
| Eight Capital, 13.5% | US$1,850 | 0.87 to 0.98 | about 1.0 | 0.98 | no solution |
| Eight Capital, 10.5% | spot | 0.48 to 0.54 | 0.49 | 0.53 | 0.67 |
| Eight Capital, 13.5% | spot | 0.65 to 0.73 | 0.65 | 0.69 | 0.86 |
| Lopatnikov and Rumyantsev (2025), 16% real WACC for this project (applied by them to probability-weighted flows) | spot | 0.85 to 0.96 | 0.84 | 0.86 | no solution |

Spot gold was US$1,961 on July 13, 2023, and about US$2,020 to US$2,036 on the three later dates. The Eight Capital opinion is dated after the July and December 15 prices.

The CIM survey's FS-stage gold rate of 8.9% already includes development risk, so it is shown as a value only. With gold flat at spot, the project is worth about US$410 million at 8.9% in July 2023 and US$449 to US$460 million on the later dates. The prices are US$131 to US$267 million.

What the readings show:

- **Fairness-opinion rates.** At the opinion's rates and gold deck, the prices are consistent with odds of roughly 0.6 to 1 that the project is built on the schedule assumed at each date. At spot gold the range is roughly 0.5 to 0.85.
- **July against December.** The market value at the DFS and the undisturbed value five months later need almost the same project-level spread to be fair, about 17% to 18%.
- **Delay at zero spread.** With no spread, implied odds fall slightly as delay is added. Waiting lowers the present value of costs but not of revenue when the convenience yield is zero (ADR 0046). The odds at zero spread are a point on the curve, not anyone's odds.

**July 2023 sensitivity.** The Q1 MD&A implies that about C$4.6 million of cash was spent between March 31 and May 29, 2023 (ADR 0048). Counting it raises the July project price by that amount. The break-even spread then moves to 16.8% to 17.7%, and the Eight Capital readings at its deck to 0.63 to 0.71 (10.5%) and 0.89 to no solution (13.5%).

**Equity floor.** The market-value readings use the equity claim, which is floored at zero on each path (ADR 0047). Existing holders can walk away rather than fund a value-destroying raise. At high spreads the floor binds on about a fifth of paths, which raised the December break-even spread from 16.9% to 18.2%, measured before the dilution correction of ADR 0048. The offers use the project claim, which is not floored.

`scripts/osino_prices.py` regenerates these figures (200,000 paths, seed 1).

## Fixed rule and optimal build timing

An optimal build rule, fitted by least-squares Monte Carlo (ADR 0038), gives the same project value as the fixed rule within about US$2 million at project-level spreads of 5%, 10% and 15%. Both rules build as soon as the project is ready. At zero spread and zero convenience yield, the optimal rule waits to the end of the window, because delay then lowers the value of capital but not of revenue; that is an artefact of those two assumptions. `scripts/build_rule_comparison.py` gives the table.

## What this is not

This is a value under stated assumptions, not a view on Osino's share price or on the takeover terms.
