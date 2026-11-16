# Gold Standard Ventures takeover: what Orla's offer implies for South Railroad

Status: Phase 3 result (#81, ADR 0043).

## The deal

Orla Mining agreed to acquire Gold Standard Ventures on June 12, 2022 and announced the deal on June 13. Each Gold Standard share received 0.1193 of an Orla share and C$0.0001. At the June 10 close this was C$0.655 per share, or C$242 million gross, a 35% premium to Gold Standard's close and to its 10-day VWAP (joint news release, June 13, 2022). The deal closed on August 12, 2022.

Gold Standard's main asset was South Railroad in Nevada, the project behind the Vox royalty (`docs/cases/south_railroad.md`). Its feasibility study (FS), released February 23, 2022, gives an after-tax NPV of US$314.8 million at 5% and US$1,650/oz gold.

The valuation date is the June 10, 2022 close. Only documents public on that date are used (ADR 0007).

## Reconciliation

The case transcribes FS Table 22-7, the detailed financial model, row by row (`cases/south_railroad_fs2022.yaml`).

- The FS discounts on a mid-year convention, with Year -1 at the valuation point. On that convention the table reproduces all four published NPVs (before and after tax, 5% and 10%) to within US$1 thousand.
- With every risk off, the engine returns the study NPV.
- Pre-tax NPVs at other gold prices match the FS sensitivity table (Table 22-6) within US$1.0 million.
- After-tax NPVs match within US$0.6 million with a marginal tax rate of 0.195 fitted to that table. The statutory rates give 0.258, which misses the table by up to 9% (ADR 0043).

## Inputs

| Input | Value | Source |
|---|---|---|
| Gold spot | US$1,871.22/oz | Alpha Vantage, status P (ADR 0024) |
| Real risk-free rate | 0.39% (10-year TIPS) | FRED DFII10 |
| US$/C$ | 1.2782 | FRED DEXCAUS |
| Volatility | 14.5% (trailing 10-year realised) | ADR 0024 |
| Convenience yield | 0, flagged | ADRs 0024, 0027 |
| Base timing | 4 years to the FS Year -1. The Notice of Intent was not yet published, so the BLM median from Notice of Intent to Record of Decision applies. The company schedule (1 year) is the sensitivity | CEQ (2020); Gold Standard release, Feb 23, 2022 (ADR 0043) |
| Capital overrun | Bertisen and Davis (2008), FS stage | ADR 0015 |
| Build rule | NPV at 5% and the current gold price at least zero, within 5 years | ADR 0023 |
| Equity issue | All-equity funding at a 10.54% discount (dilution upper bound) | Carpentier and Suret (2009) (ADR 0030) |

## Prices

Balance-sheet items come from Gold Standard's interim statements at March 31, 2022, the latest published before the offer:

- cash C$17.49 million, lease liabilities C$0.36 million, no borrowings;
- 358.7 million shares and 4.2 million restricted share units, which vest under the arrangement;
- 18.4 million options, of which only the 4.8 million granted at C$0.57 in Q1 2022 are in the money.

Silver revenue in the FS is already net of the 2020 Orion silver stream, so the stream deposit is not treated as debt. Gold Standard's other ground (Lewis, North Railroad) is valued at zero, so the implied odds are an upper bound for South Railroad alone.

- **Orla's offer:** C$221.0 million (US$172.9 million) for the project claim. The acquirer funds construction (ADR 0031). The price includes any control premium and synergies, so it overstates the odds on a standalone basis.
- **Undisturbed market value, June 10, 2022:** C$0.485 per share, implied by the stated 35% premium to the close. This gives C$159.0 million (US$124.4 million) for the equity claim with dilution (ADR 0030). Corporate G&A of C$9.1 million a year, the Q1 2022 figure annualised, is deducted over the mine life (ADR 0033).

## What the prices imply

As for Osino, each price is shown against a real spread on net project cash flows (ADR 0032). The odds are those of passing the remaining gates at zero added delay, under each timing assumption.

| Real spread | Offer, 4 years | Undisturbed, 4 years | Offer, 1 year | Undisturbed, 1 year |
|---|---|---|---|---|
| 0% | 0.29 | 0.30 | 0.30 | 0.28 |
| 4% | 0.41 | 0.46 | 0.38 | 0.37 |
| 8% | 0.57 | 0.72 | 0.47 | 0.50 |
| 12% | 0.79 | above 1 | 0.59 | 0.67 |
| 15% | 0.99 | above 1 | 0.69 | 0.86 |
| Break-even | 15.1% | 10.8% | 22.1% | 16.8% |

The study's own rates are read the way the study used them: gold flat at the FS deck of US$1,650, discounted at the rate, with this engine's stage and overrun risks on top (ADR 0045).

| Study rate, gold flat at US$1,650 | Offer, 4 years | Undisturbed, 4 years | Offer, 1 year | Undisturbed, 1 year |
|---|---|---|---|---|
| FS base case, 5% | 0.74 | 0.93 | 0.64 | 0.70 |
| FS sensitivity table, 10% | no solution | no solution | 0.87 | 0.98 |

The timing assumption matters as much as the rate. Under the 4-year prior, the market value before the offer is consistent with certain passage at a market-consistent real spread of about 11%. Under the company's schedule, the same price needs a spread of about 17%. One price cannot separate the odds from the timing, so both are reported.

The undisturbed reading uses the equity claim, floored at zero on each path (ADR 0047). The floor raised its break-even spread from 10.0% to 10.8% (4 years) and from 15.5% to 16.8% (1 year). The offer uses the project claim, which is not floored.

**Sensitivity: the LBMA PM gold price (ADR 0050).** The snapshot uses the June 10, 2022 closing gold price, US$1,871. The LBMA PM fix that day was US$1,830, 2.2% lower. June 10, 2022 was a US CPI release day, and gold rallied after the London fix into the New York close. The closing price is kept because the share prices read here are closing prices: a 4 pm New York gold price implied by the GLD trust is within 0.1% of it. At the LBMA PM the break-even spreads fall:

| | Offer, 4 years | Undisturbed, 4 years | Offer, 1 year | Undisturbed, 1 year |
|---|---|---|---|---|
| Closing price (headline) | 15.1% | 10.8% | 22.1% | 16.8% |
| LBMA PM | 14.2% | 10.0% | 20.4% | 15.5% |

The odds at the study's own rates do not change, because those rows hold gold flat at the FS deck.

`scripts/gsv_takeover.py` regenerates every figure (200,000 paths, seed 1). The sensitivity was run by setting `gold_spot` to the snapshot's `gold_lbma_pm` value.

## Outcome tracking

The following dates come after the valuation date. They are not used in the valuation.

- The Notice of Intent was published in the Federal Register in August 2025.
- The Record of Decision was announced on August 17, 2026, about 4.2 years after the valuation date.

## What this is not

This is a value under stated assumptions. It is not a view on the offer terms, on either company's share price, or on whether the price was high or low.
