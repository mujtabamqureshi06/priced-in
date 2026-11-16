# Orla Mining sum of parts: South Railroad inside a producer

Status: Phase 3 result (#75, ADR 0044).

## The question

After Orla Mining closed its acquisition of Gold Standard Ventures on August 12, 2022, South Railroad was one asset inside a producing company. Can its price be read out of Orla's market value? The method takes enterprise value, adds back corporate G&A, and takes out the parts the market can see. What is left is an upper bound on what the market paid for South Railroad's plan.

## Inputs (US$ million, August 12, 2022)

| Item | Value | Source |
|---|---|---|
| Share price | US$3.4188 | Fair value of the 43.7 million shares issued at closing (Orla Q3 2022 statements, note 12) |
| Diluted equity value | 1,086.7 | 303.3 million basic shares and share units, plus in-the-money options and warrants by the treasury method (Orla June 30, 2022 statements) |
| Net debt | 88.2 | Credit facility 129.2 and Fresnillo obligation 37.8, plus leases 1.3, less Orla cash 66.7 and Gold Standard cash of C$17.1 million (March 31, 2022) |
| Enterprise value | 1,174.9 | |
| Corporate G&A, PV | 191.8 | US$11.7 million a year (first half of 2022, annualised) over 17 years at the real rate (ADR 0033) |
| Camino Rojo | By spread, below | January 2021 feasibility study, remaining after-tax cash flows from the valuation date, re-priced at the expected gold price |
| Cerro Quema | 0 to 231.3 | July 2021 pre-feasibility study NPV at the spot gold price, interpolated from its sensitivity table, unrisked |
| Gold spot, real rate, US$/C$ | US$1,801.60; 0.37%; 1.2783 | Snapshot 2022-08-12 (ADR 0024) |

Exploration ground and resources outside the study plans are valued at zero. That includes the Camino Rojo sulphides below the oxide pit.

## Result

| Real spread | Camino Rojo | South Railroad price | South Railroad value if built on schedule | Implied odds |
|---|---|---|---|---|
| 0% | 838.0 | 297.3 to 528.6 | 538.1 | 0.55 to 0.98 |
| 4% | 723.7 | 411.7 to 643.0 | 379.5 | above 1 |
| 8% | 633.6 | 501.8 to 733.1 | 271.3 | above 1 |
| 12% | 561.6 | 573.8 to 805.1 | 196.0 | above 1 |
| 15% | 516.7 | 618.6 to 849.9 | 154.5 | above 1 |

The band comes from Cerro Quema: its low end takes Cerro Quema at its study NPV, its high end at zero. South Railroad's value uses the 2022 feasibility study and the 4-year timing prior (ADR 0043), read against the project claim (ADR 0047).

## Reading

At any positive spread, the residual is larger than South Railroad would be worth even if it were certain to be built on schedule. Orla's market value was well above the sum of its published plans. A sum of parts cannot say which asset carries that excess. Candidates include unplanned resources, exploration, and expectations for Camino Rojo beyond its oxide study. So the band does not identify South Railroad's odds.

For South Railroad itself, the single-asset reading of Orla's offer (`docs/cases/gold_standard_takeover.md`) is the one to use. This case shows the limit of the method for a producer with large unplanned resources. It does not claim the market price is wrong.

`scripts/orla_sum_of_parts.py` regenerates every figure (200,000 paths, seed 1). Inputs and their sources are in `data/sum_of_parts/orla_2022-08-12.yaml`.

## Limits

- Camino Rojo's annual table does not reproduce its published NPV (US$471.6 million against US$452 million at 5%). The study does not state the timing of capital already spent. Only flows after the valuation date are used.
- Camino Rojo's 2022 cash flows are assumed to fall evenly through the year. The study's Year 1 is taken as calendar 2022, since commercial production began in April 2022.
- Gold Standard's cash is its March 31, 2022 balance, and its spending to closing is not deducted. At its first-quarter rate (C$5.2 million) this is about US$6 million, small against the band.
