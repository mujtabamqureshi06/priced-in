# Sorby Hills: what the Vox royalty price implies

## The deal

On September 28, 2026, Vox Royalty agreed to buy an effective 0.75% net smelter return (NSR) royalty over Boab Metals' Sorby Hills silver-lead project in Western Australia. The price is US$13.0 million in cash, paid to a private seller. Completion depends on Foreign Investment Review Board approval.

At the deal date the project was past its final investment decision (December 2025), fully funded and in construction. Boab targeted first concentrate in the second half of 2027.

The latest public mine plan is the June 2024 front-end engineering and design (FEED) study. In December 2025 Boab stated that its production targets and financial forecasts continue to apply.

## What is being asked

The construction decision has been made. So the question is not whether the mine will be built, but what odds of reaching production on the FEED schedule the price implies, given the return the buyer requires.

As for South Railroad, one price cannot separate odds from the required return. The results are therefore shown across a range of required returns.

## Inputs and their sources

| Input | Value | Source |
|---|---|---|
| Price | US$13.0M | Vox release, September 28, 2026 |
| Royalty | 0.75% of project NSR, all payable metals (silver and lead), whole FEED schedule | Vox release; ADR 0035 |
| NSR base | Revenue less lead treatment and silver refining charges | FEED Table 10; ADR 0035 |
| Schedule | FEED annual table, 2027 to 2035; 17.2 Moz payable silver and 546 kt payable lead; 17% of ore mined is Inferred | FEED Tables 10 and A11 |
| Timing | First production year paid two years after the deal date | ADR 0035 |
| Silver spot | US$60.81/oz | Alpha Vantage daily series, status P |
| Lead spot | US$1,886/t (LME cash); 3-month US$1,911.5/t | Westmetall, status P |
| Real risk-free rate | 2.90% (10-year TIPS) | FRED DFII10 |
| Convenience yields | 0 for both metals; plus and minus 2% as sensitivities | ADR 0035 |

The FEED deck is US$27.5/oz silver and US$2,251/t lead in the long run, with A$:US$ at 0.68. On the deal date silver traded at more than twice that deck and lead at about 16% below it.

## How the value is computed

Revenue for each metal in the FEED table is converted to US$ at the study's own exchange rate and rescaled from the FEED price to the market's expected price. The treatment and refining charges stay at the FEED schedule.

Under market prices, a metal's expected price grows at the real risk-free rate less its convenience yield. Each year's royalty is discounted at the real rate plus the buyer's spread.

Once the build decision has been made, the value is linear in prices, so volatility and the silver-lead correlation do not change it. A correlated simulation checks the closed form (ADR 0036).

## Results

Implied odds equal the price divided by the value if production follows the FEED schedule.

| Buyer's real spread | Value if production follows the FEED schedule (US$M) | Implied odds of reaching production on the FEED schedule |
|---|---|---|
| 0% | 14.74 | 0.88 |
| 2% | 13.23 | 0.98 |
| **2.33% (break-even)** | **13.00** | **1.00** |
| 4% | 11.92 | price above this value |
| 8% | 9.79 | price above this value |
| 16% | 6.88 | price above this value |

Reference points, each converted to a spread at this deal's date:

| Reference | Spread | Value (US$M) | Implied odds |
|---|---|---|---|
| OR Royalties (formerly Osisko), 2025 audited statements, post-tax real 5.1% (IAS 36; one company; not a purchase price) | 2.2% | 13.09 | 0.99 |
| Same, grossed up to pre-tax at the 26.5% statutory rate (approximation) | 4.0% | 11.89 | price above this value |
| Wharf control (Metalla, 2020) | 15.8% | 6.95 | price above this value |

At the raw OR Royalties spread (2.2%), the price implies odds of 0.99 if production starts on time. With one year of delay or more, the price is above the value at that spread.

## Reading the result

The price equals the value of the FEED schedule built on time at a real spread of 2.3% over Treasury inflation-protected yields. At royalty-company rates converted to this date (about 2% to 4%), the price is consistent with near-certain completion on schedule. That is the expected pattern for a funded project in construction.

At higher required returns, the price is above the value of the FEED schedule. Possible readings, none of which the price alone can separate:

- the buyer requires a lower return than the spread used;
- the buyer counts value beyond the FEED schedule, such as the reserve and mine-life additions from drilling that the release says would be royalty-linked;
- the buyer expects metal prices above the market forward, or a lower convenience yield;
- the royalty base is wider than modelled (for example, other metals or ground outside the FEED plan).

These are readings of the price, not judgments on the deal.

## Sensitivities

All at the OR Royalties pre-tax spread (4.0%) unless stated.

| Case | Value (US$M) | Break-even spread |
|---|---|---|
| Base | 11.89 | 2.3% |
| First production year paid one year after the deal | 12.34 | 2.8% |
| Logistics also deducted from NSR | 11.48 | 1.7% |
| Silver only | 6.23 | none: the price is above the value even at 0% |
| Convenience yield +2% (both metals) | 10.61 | 0.1% |
| Convenience yield -2% (both metals) | 13.36 | 4.6% |
| Lead convenience yield from LME cash to 3-month, -1.1% (short-tenor proxy) | 12.29 | 3.0% |

The silver-only reading cannot reproduce the price at any non-negative spread. This supports reading the royalty as covering all payable metals, but that remains an inference until the terms are disclosed.

## Limits

1. **Metals covered and "effective".** Neither is stated in the release. 0.75% matches a 1% NSR on the 75% interest Boab held when it acquired the project (Boab half-year report, Note 14). This is an inference.
2. **Schedule age.** The schedule is from 2024. The December 2025 plant change cut capital and time but, by Boab's statement, not the production targets.
3. **Inferred material.** 17% of the ore mined in the FEED schedule is Inferred.
4. **Price inputs.** Silver and lead spot are vendor and secondary series (status P), not the LBMA or LME official publications.
5. **Taxes.** Australian withholding and the buyer's own taxes are not modelled; the spread is compared with pre-tax and post-tax reference rates for this reason.
6. **Timing.** Whole years only, with each year paid at its end.

Regenerate every number with `uv run python scripts/sorby_hills_case.py`.
