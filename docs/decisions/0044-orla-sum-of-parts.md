# 0044. Orla Mining sum of parts

- Status: accepted
- Date: 2026-11-16

## Context

ADR 0042 set the multi-asset test for v1.0: read South Railroad out of Orla Mining's market value after Orla closed its acquisition of Gold Standard Ventures, and show the result as a band (#75).

## Decision

1. **Valuation date: August 12, 2022, the closing date.**
   - Orla's June 30, 2022 statements are the latest balance sheet published before that date. Gold Standard's March 31, 2022 statements give its cash.
   - The share price is the fair value of the shares Orla issued at closing, US$3.4188. This is a market observation on the date, recorded in Orla's Q3 2022 statements; no other later information is used.
   - Options, warrants and share units enter by the treasury method at the closing FX rate.
2. **Parts.**
   - **Camino Rojo (producing).** Valued on its January 2021 feasibility study's remaining after-tax cash flows, from the valuation date to closure, re-priced at the expected gold price under the market-consistent drift (`pricedin.sum_of_parts.producing_value`). It is discounted at the same real spread as South Railroad. The Mexican special mining duty and income tax give a marginal rate of 0.3525. The study's published NPV is not reproduced from its annual table (US$471.6 million end-year against US$452 million): the timing convention for capital already spent is not stated. Only flows after the valuation date are used.
   - **Cerro Quema (pre-feasibility).** A range from zero to the study NPV at the spot gold price, unrisked. No schedule is transcribed, so this end is at the study's 5% rate.
   - **Corporate G&A.** The first-half 2022 figure, annualised, over South Railroad's horizon, discounted at the real rate, as for Osino (ADR 0033). It is added back to enterprise value, since the market price is net of it.
   - **Exploration ground and resources outside the study plans** (including the Camino Rojo sulphides): zero. The residual is therefore an upper bound on what the market pays for South Railroad's plan.
3. **Reading.** Each end of the band is read as implied odds against the South Railroad project claim at the same spread, on the 2022 feasibility study and the 4-year timing prior (ADR 0043).

## Consequences

The residual exceeds South Railroad's on-schedule value at every positive spread. The market valued Orla well above the sum of its study plans, and a sum of parts cannot assign that excess to one asset. The band is reported as an upper bound and is not used to identify South Railroad's odds; the single-asset takeover reading (ADR 0043) is the one to use. This is the expected limit of the method for a producer with large unplanned resources, and it is stated in the write-up.
