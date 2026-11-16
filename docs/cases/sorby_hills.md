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
| Royalty | 0.75% of project NSR, all payable metals (silver and lead), whole FEED schedule. Coverage of lead is an inference: Vox titles the deal a silver royalty over a silver-lead project | Vox release; ADR 0035 |
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

Reference points are read the way their source used them: metal prices flat in real terms at the source's own deck, discounted at the stated rate (ADR 0045). OR Royalties states a long-term silver price (US$42/oz) but no lead price, so lead is held at spot.

| Reference | Prices | Value, silver and lead (US$M) | Value, silver only (US$M) | Implied odds |
|---|---|---|---|---|
| OR Royalties (formerly Osisko), 2025 audited statements: post-tax real 5.1% in its goodwill test (fair value less costs of disposal; one company; not a purchase price) | Silver US$42, lead spot | 9.24 | 3.99 | price above this value |
| Same | Spot | 11.09 | 5.84 | price above this value |
| Same, grossed up to pre-tax 6.94% at the 26.5% statutory rate (approximation) | Silver US$42, lead spot | 8.42 | 3.64 | price above this value |
| Same | Spot | 10.11 | 5.32 | price above this value |
| Wharf control (Metalla, 2020), market-consistent spread 15.8% | Market-consistent | 6.95 | | price above this value |

## Reading the result

The price equals the value of the FEED schedule built on time at a market-consistent real spread of 2.3% over Treasury inflation-protected yields. That assumes the royalty covers silver and lead.

At OR Royalties' own rate and price deck, the value of the FEED schedule built on time is below the price, so no odds reconcile the price at that rate, even with certain completion. The same holds at spot prices and at the pre-tax rate. On a silver-only reading the gap is wider.

So the price cannot be read as near-certain completion at royalty-company rates. Possible readings, none of which the price alone can separate:

- the buyer requires a lower return than the royalty-company reference rate;
- the buyer counts value beyond the FEED schedule, such as the reserve and mine-life additions from drilling that the release says would be royalty-linked;
- the buyer expects metal prices above the deck used, or a lower convenience yield;
- the royalty base is wider than modelled (for example, other metals or ground outside the FEED plan).

These are readings of the price, not judgments on the deal.

## Sensitivities

In market-consistent mode, at a round 6% real spread for comparison.

| Case | Value (US$M) | Break-even spread |
|---|---|---|
| Base | 10.78 | 2.3% |
| First production year paid one year after the deal | 11.39 | 2.8% |
| Logistics also deducted from NSR | 10.40 | 1.7% |
| Silver only | 5.64 | none: the price is above the value even at 0% |
| Convenience yield +2% (both metals) | 9.64 | 0.1% |
| Convenience yield -2% (both metals) | 12.08 | 4.6% |
| Lead convenience yield from LME cash to 3-month, -1.1% (short-tenor proxy) | 11.13 | 3.0% |

The silver-only reading cannot reproduce the price at any non-negative spread. This supports reading the royalty as covering all payable metals, but that remains an inference until the terms are disclosed.

## Limits

1. **Metals covered and "effective".** Neither is stated in the release, which titles the deal a silver royalty over a silver-lead project. 0.75% matches a 1% NSR on the 75% interest Boab held when it acquired the project (Boab half-year report, Note 14). This is an inference.
2. **Schedule age.** The schedule is from 2024. The December 2025 plant change cut capital and time but, by Boab's statement, not the production targets.
3. **Inferred material.** 17% of the ore mined in the FEED schedule is Inferred.
4. **Price inputs.** Silver and lead spot are vendor and secondary series (status P), not the LBMA or LME official publications.
5. **Taxes.** Australian withholding and the buyer's own taxes are not modelled; the price is read at both the pre-tax and the post-tax reference rate for this reason.
6. **Timing.** Whole years only, with each year paid at its end.

Regenerate every number with `uv run python scripts/sorby_hills_case.py`.
