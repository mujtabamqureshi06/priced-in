# Phase 2 back-test: what public prices imply about build odds

Released with v0.2.0 (#74).

## 1. Question

A royalty, a developer's market value or a takeover bid is a price on an undeveloped mine. Technical studies give a net present value (NPV) that assumes the mine is built on schedule. The price is usually far below it.

This back-test asks what each price implies about the odds that the mine is built, and when, once the engine has valued the claim on the same simulated futures. It does not ask whether any price was right.

## 2. Method in brief

The full method is in `docs/methodology.md`. The steps that matter here:

1. **Market-consistent values.** Metal prices follow geometric Brownian motion with drift equal to the real risk-free rate less a convenience yield. Cash flows are discounted at the real risk-free rate plus a stated spread (ADRs 0012, 0024). There is no distribution of NPVs at a risk-adjusted rate (Davis 1995).
2. **Odds are linear in value.** Paths that fail a stage gate pay nothing except any advance royalties, so for each added delay the implied odds have a closed form: price less the value on failing paths, divided by the value on passing paths less the value on failing paths (ADR 0023).
3. **One price, two unknowns.** A price cannot separate odds from timing. Every result is a frontier of odds against delay, summarised by the zero-delay odds (ADR 0023).
4. **The required return.** It is not observed. Each result is shown across a range of real spreads. It is marked at the break-even spread, where the price equals the value of certain, on-schedule construction, and at reference rates converted to spreads at each deal's date (ADRs 0028, 0032, 0035).
5. **Claims match prices.**
   - A royalty price is compared with the royalty claim.
   - An undisturbed market value is compared with the equity claim, with dilution and corporate costs.
   - A takeover bid is compared with the project claim, since the acquirer funds construction (ADRs 0030, 0031, 0033).

## 3. Data

`data/transactions.csv` lists every deal considered, with sources (#73, ADR 0034). Only deals with a public economic study at the deal date are modelled.

| Deal | Date | Price | Stage | Use |
|---|---|---|---|---|
| South Railroad 0.633% NSR (Vox) | June 7, 2021 | US$2.079M incl. finder's fee | PFS (2020) | Modelled |
| Sorby Hills effective 0.75% NSR (Vox) | Sept 28, 2026 | US$13.0M | In construction; FEED (2024) | Modelled |
| Wharf 1.0% GVR (Metalla) | June 22, 2020 | US$6.11M incl. shares and costs | Producing | Control |
| White Dam 2.0% NSR (Vox) | Sept 2, 2026 | A$5.0M | Producing from the historical pad; no study | Listed only |
| Kalman and Sylvania (Vox) | Aug 20, 2026 | A$3.4M for both | Development and exploration | Listed only |
| Federation and a copper tonnage royalty (Vox) | Feb 26, 2026 | up to A$0.65M | Mixed | Listed only |

Osino Twin Hills adds three equity prices on one project, each with Osino's own September 30, 2023 balance sheet (ADR 0033):

- the undisturbed market value on December 15, 2023;
- Dundee Precious Metals' offer (December 18, 2023);
- Shanjin's offer (February 23, 2024).

Market inputs are dated snapshots in `data/snapshots/`. No observation postdates its valuation date (ADR 0007).

## 4. Results

| Case | Claim | Break-even real spread | Reference rate (converted at the deal date) | Zero-delay implied odds at the reference |
|---|---|---|---|---|
| South Railroad (PFS) | Royalty with advance royalties | 8.3% | Osisko 2020, 3.5% post-tax real: 4.3% raw, 5.6% pre-tax | 0.72 to 0.80 |
| Osino, undisturbed (DFS) | Equity, diluted, less G&A | 16.8% | Eight Capital fairness opinion, 10.5% to 13.5% real: 8.8% to 11.8% | 0.38 to 0.53 |
| Osino, Dundee offer | Project | 19.6% | Same | 0.40 to 0.51 |
| Osino, Shanjin offer | Project | 17.2% | Same | 0.48 to 0.62 |
| Sorby Hills (construction) | Royalty, all payable metals | 2.3% | OR Royalties 2025, 5.1% post-tax real: 2.2% raw, 4.0% pre-tax | 0.99 at the raw rate; at the pre-tax rate the price is above the certain value |

Royalty spreads and project-level spreads are not the same quantity. A royalty carries no capital or operating cost risk; the project claim does. The two kinds of reference rate are therefore not comparable across rows. Within each row, the reading is the same: what the odds are at the stated required return.

### What happened afterwards (outcome tracking only)

None of these outcomes is used in any valuation.

- **South Railroad.** The Bureau of Land Management Record of Decision was announced on August 17, 2026, by Equinox Gold, which now owns the project; first gold is targeted for 2028. Base timing at the 2021 deal assumed construction could start about four years after the deal date (ADR 0023). Construction could not start before the Record of Decision, about five years after the deal, so the outcome lies at one or more years of added delay on the frontier, where the implied odds for the same price are higher.
- **Osino.** Shanjin completed the acquisition on August 29, 2024. Namibian press reports Twin Hills in construction in 2025 and 2026 (secondary sources, status P).
- **Sorby Hills.** Too recent. First concentrate is targeted for the second half of 2027.

## 5. Control behaviour

**Wharf.** The one qualifying producing-royalty purchase implies a 15.8% real spread (ADR 0026). That is far above the 2% to 6% the royalty companies' own impairment-test rates give once converted to spreads. Four reasons, all stated with the control:

1. Its cash flows are built from reserves only, so the spread is an upper bound on the true one (a lower bound on value).
2. 81% of the price was paid in the buyer's shares.
3. It is one deal on one date.
4. The impairment rates are value-in-use rates for royalties a company already holds, not purchase prices.

The deviation is explained rather than resolved. A second control remains open (ADR 0028).

**White Dam.** It was planned as a second control, but it cannot be one. At the deal date there was no published mine plan for the royalty ground (ADR 0034).

**Sorby Hills as the high-odds check.** The build plan expected a funded project in construction to imply near-certain odds. At royalty-company rates converted to the deal date, it does: odds of 0.99, or a price above the certain value at the pre-tax rate. That holds only if the royalty covers all payable metals. A silver-only reading cannot reproduce the price at any spread (ADR 0035).

## 6. Synthetic recovery

For each adapter, prices are generated from the engine with known odds, and the solver recovers those odds. The tests are:

- royalty with advance royalties: `tests/test_inversion.py`;
- equity and project claims: the `equity_frontier` tests in `tests/test_inversion.py`;
- multi-metal royalty: `tests/test_royalty_cases.py`.

Each test also checks the cases with no solution: a price above the certain, on-schedule value is reported as "no solution", never as a probability above one (ADR 0025). The frontier shape test allows for Monte Carlo error on common paths.

## 7. What the results say and do not say

**They say:**

1. **The required return dominates.** In every case, moving the spread across a plausible range moves the implied odds more than any other input. A price can only be read jointly with a stated required return. That is why every result is a curve, with the break-even marked.
2. **The ordering by stage is as expected.** At reference rates converted to each deal's date, implied odds rise with stage:
   - about 0.7 to 0.8 for a PFS-stage royalty;
   - about 0.4 to 0.6 for a DFS-stage developer and its bidders, on project-level spreads that also price capital and operating risk;
   - about 1 for a funded project in construction.
3. **Delay is cheap for royalties.** For a royalty valued at market prices, waiting costs the holder only the spread plus the convenience yield, so moderate delays change the implied odds by a few points per year.

**They do not say:**

- that any buyer paid too much or too little;
- that the market is wrong;
- that the studies are wrong;
- that implied odds predict construction. Three projects cannot test that; Phase 4 asks it on a panel.

The numbers are not "the market's odds". They are the odds consistent with each price under the stated required return and the study's own mine plan.

## 8. Limits

1. **Few cases.** Two royalties, one project with three equity prices, and one control.
2. **Reference rates.** They come from accounting disclosures and a fairness opinion, not from observed purchase prices, and the conversion to pre-tax rates is approximate.
3. **Value beyond the study mine plan is not modelled.** It would raise the value and lower the implied odds. Resources outside the plan exist at South Railroad and Sorby Hills.
4. **Convenience yields are zero by default.** The break-even spread moves by about one point per point of yield (Sorby Hills sensitivity).
5. **Ramp-up is not modelled** (ADR 0029). Time runs in whole years.
6. **Some price inputs are secondary** (status P): vendor gold and silver series, and a secondary publication of LME lead prices.
7. **Osino's July 2023 developer value is not yet computed.** The circular gives the July 2023 trading range (C$1.07 to C$1.20, p. 109), but the last balance sheet published before that date (March 31, 2023) has not yet been retrieved.

## 9. Reproduce

`uv run python scripts/backtest.py` prints every number above. It runs:

- the Wharf control;
- `scripts/south_railroad_case.py`;
- `scripts/osino_prices.py`;
- `scripts/sorby_hills_case.py`;
- the dataset summary.

Fixed seeds; about 15 seconds.

## Sources

Every source is listed with its location and verification status in `docs/sources.md`. The case notes give the case-level detail:

- `docs/cases/south_railroad.md`;
- `docs/cases/osino_twin_hills.md`;
- `docs/cases/sorby_hills.md`.
