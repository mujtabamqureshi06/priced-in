# South Railroad: what the Vox royalty price implies

Status: wording approved by the owner on 2026-11-16 (ADR 0028). The repository is private; publication follows the owner's decision to make it public.

## The deal

On June 7, 2021, Vox Royalty bought a 0.633% NSR royalty on part of Gold Standard Ventures' South Railroad project in Nevada for US$1.98 million in cash plus a US$99,000 finder's fee: US$2.079 million in all (ADR 0020). The royalty covers about 35% of the project's resource (ADR 0016) and carries advance minimum royalties of C$120,000 a year until production (ADR 0021). The project's latest study at that date was the 2020 pre-feasibility study (PFS).

## What the engine does

It values the royalty on thousands of simulated futures of the PFS mine plan, using market prices on June 7, 2021 (ADR 0024), and asks: for the price to be fair, what odds of construction does it imply, and how late could construction be? One price cannot answer both at once, so the answer is a line of odds against delay (the frontier), not a single number.

## Inputs and their sources

| Input | Value | Source |
|---|---|---|
| Price | US$2.079M (US$2.317M capitalised cost as sensitivity) | Vox release, June 7, 2021; Vox 2022 audited statements (ADR 0020) |
| Royalty | 0.633% NSR, 35% of the mine plan's gold, uniform | Vox filings (ADR 0016) |
| Advances | C$120,000 a year, fixed nominal, valued at the Government of Canada 10-year yield (1.47%) and USD/CAD 1.2062 | ADRs 0021, 0024 |
| Gold spot | US$1,898.50/oz | Alpha Vantage daily series, status P (ADR 0024) |
| Real risk-free rate | -0.82% (10-year TIPS) | FRED DFII10 |
| Gold convenience yield | 0, flagged; 1% sensitivity | ADRs 0024, 0027 |
| Gold volatility | 14.8% (trailing 10-year realised) | ADR 0024 |
| Base timing | 4 years to the PFS Year -1 | CEQ (2020) BLM EIS median (ADR 0023) |
| Build rule | Build when after-tax NPV at 5% and the current gold price is at least zero, within 5 years | ADR 0023 |
| Capital overrun | Bertisen and Davis (2008) applied to a PFS estimate, flagged | ADR 0015 |
| Ramp-up | Not modelled | ADR 0029 |

## Disclosures required before any result is shown

1. **Advance royalties** are paid every year from the deal date until production on paths that are built, including any delay. On paths that fail a stage gate they stop at the base build-ready year; on paths the build rule never builds they stop when the 5-year window closes (ADRs 0021, 0025). If operators give up ground sooner or renegotiate, this overstates value and pushes implied odds lower.
2. **Crediting:** the headline treats advances as credited against later royalties, an interpretation of the term "advance", not a disclosed term. The not-credited case is shown alongside (ADR 0021).
3. **Buy-down:** none assumed, which overstates value and pushes implied odds lower (ADR 0021).
4. **The advance amount** is treated as fixed at C$120,000; if it is a floor, value is understated and implied odds are pushed higher.
5. **Failure timing:** a failing project fails on the original schedule; the delay axis means "years late, for a project that is built". If failing projects linger and keep paying advances, implied odds are slightly overstated (ADR 0025).
6. **Cost of delay:** for a gold royalty under market prices, waiting costs the holder the buyer's spread s plus the gold convenience yield y. Here y = 0, and the gold convenience yield was not checked against futures prices. Gold's convenience yield is assumed similar on the control's and the target's dates (ADRs 0024, 0027).
7. **Outcome dates** after June 7, 2021 (the BLM Notice of Intent in August 2025 and the later Record of Decision) are not used; they are for outcome tracking only (ADR 0023).
8. **Existing royalty burden:** the PFS cash flow already deducts a 1.24% existing royalty burden, which probably includes this royalty; to be confirmed.

## The buyer's required return decides the answer

ADR 0014 calibrates the buyer's required return (a real spread over the risk-free rate) on purchases of royalties on producing mines. Only one such purchase qualifies so far (ADR 0026), so the spread is not fixed (ADR 0028). The table shows the zero-delay implied odds, the lowest build odds consistent with the price if the project keeps to the schedule assumed at the valuation date, across spreads.

| Real spread | Zero-delay odds, advances credited | Not credited |
|---|---|---|
| 0% | 0.49 | 0.44 |
| 2% | 0.59 | 0.53 |
| 4% | 0.70 | 0.62 |
| 6% | 0.83 | 0.73 |
| 8% | 0.97 | 0.86 |
| 10% | no solution | 1.00 |
| 12% and above | no solution | no solution |

"No solution" means the price is above the value of the royalty with certain, on-schedule construction under the PFS plan.

**Break-even spread:** 8.3% at the US$2.079M price; 6.8% at the US$2.317M capitalised cost. Below it, some odds below one reconcile the price on schedule; above it, none do on the PFS plan.

| Reference point | Real spread | Zero-delay odds (credited) |
|---|---|---|
| Osisko Gold Royalties, 2020 audited statements, post-tax real 3.5% for its producing Canadian NSR royalties (IAS 36 value in use; one company; not a purchase price) | 4.3% | 0.72 |
| Same, grossed up to pre-tax at Osisko's 26.5% statutory rate (approximation ignoring depletion shields) | 5.6% | 0.80 |
| Wharf, the one qualifying producing-royalty purchase (Metalla, 2020; reserve-only flows, so a lower bound; 81% paid in shares) | 15.8% | no solution |

## Odds against delay at the Osisko reference rate

Advances credited:

| Years late | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 |
|---|---|---|---|---|---|---|---|---|---|
| Spread 4.3% | 0.72 | 0.75 | 0.77 | 0.80 | 0.83 | 0.85 | 0.87 | 0.92 | 0.95 |
| Spread 5.6% | 0.80 | 0.84 | 0.87 | 0.92 | 0.96 | 1.00 | n/s | n/s | n/s |

At 5.6%, the price is consistent with certain construction only with a delay of at least about 5 years. At 4.3% it is consistent with odds below one for every delay up to 10 years. Not credited, the odds are lower (0.64 to 0.76 at 4.3%; 0.71 to 0.92 at 5.6%) and certain construction is not reached within 10 years. Every frontier rises with delay (tested allowing for Monte Carlo noise).

All figures use 20,000 paths and seed 1; `scripts/south_railroad_case.py` regenerates them.

## Reading the result

Wording for owner review (ADR 0028):

> What this price implies about build odds depends mainly on the return the buyer required. At a royalty company's own valuation rate for producing royalties, it is consistent with odds of about 0.7 to 0.8 that the project is built on the schedule assumed at the valuation date. At the spread implied by the one qualifying producing-royalty purchase, the value of the PFS mine plan with certain, on-time construction is below the price, so odds and timing cannot account for the price on that plan alone. Possible reasons include value outside the PFS mine plan, since the royalty area includes resources beyond the PFS reserve, or different required returns across buyers and dates.

These numbers are not "the market's odds", and nothing here suggests any party paid too much or too little.

## What would change it

- A second qualifying producing-royalty control (Houndé is being checked).
- Impairment-test rates from other royalty companies.
- A futures-based gold convenience yield for June 2021.
- Ramp-up, not modelled (ADR 0029).
