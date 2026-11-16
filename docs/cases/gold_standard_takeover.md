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
| 0% | 0.30 | 0.32 | 0.30 | 0.29 |
| 4% | 0.42 | 0.50 | 0.38 | 0.39 |
| 8% | 0.58 | 0.80 | 0.47 | 0.53 |
| 12% | 0.80 | above 1 | 0.59 | 0.73 |
| 15% | above 1 | above 1 | 0.69 | 0.95 |
| Break-even | 14.9% | 9.7% | 22.1% | 15.5% |

Reference points, as real rates converted to spreads:

| Reference rate | Spread | Offer, 4 years | Undisturbed, 4 years | Offer, 1 year | Undisturbed, 1 year |
|---|---|---|---|---|---|
| FS 5% | 4.6% | 0.44 | 0.54 | 0.39 | 0.40 |
| FS 10% | 9.6% | 0.66 | 0.98 | 0.52 | 0.60 |

The timing assumption matters as much as the spread. Under the 4-year prior, the market value before the offer is consistent with certain passage at a real spread of about 10%. Under the company's schedule, the same price needs a spread of about 15%. One price cannot separate the odds from the timing, so both are reported.

`scripts/gsv_takeover.py` regenerates every figure (20,000 paths, seed 1).

## Outcome tracking

The following dates come after the valuation date. They are not used in the valuation.

- The Notice of Intent was published in the Federal Register in August 2025.
- The Record of Decision was announced on August 17, 2026, about 4.2 years after the valuation date.

## What this is not

This is a value under stated assumptions. It is not a view on the offer terms, on either company's share price, or on whether the price was high or low.
