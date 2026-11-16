# Sources register

Every source that feeds a prior or a test case, with its verification status and where the figure sits. Third-party documents are not stored in this repository (ADR 0003).

Status: **[V]** verified against the primary document or the issuer's own release. **[V-abs]** verified from the abstract or citation only; the full text is still needed for the specific figure. **[S]** seen only in a secondary summary; do not cite publicly. **[P]** practitioner or industry source, not peer-reviewed. **[X]** do not use.

Last full review: 2026-11-16.

## 1. Test cases

### 1.1 Osino Twin Hills (Namibia, gold)

| Fact | Value | Source and location | Status |
|---|---|---|---|
| DFS announcement date | June 12, 2023 | Osino news release, June 12, 2023 (GlobeNewswire) | [V] |
| DFS NPV5 at US$1,750/oz | Pre-tax US$742M; post-tax US$480M | Same release, Table 1 | [V] |
| DFS IRR at US$1,750/oz | 34% pre-tax; 28% post-tax | Same release, Table 1 | [V] |
| DFS NPV5 at US$1,950/oz | Pre-tax US$1,024M; post-tax US$656M | Same release, Table 1 | [V] |
| Initial capital | US$365M, including US$34M contingency and US$18M capitalised pre-strip | Same release, highlights | [V] |
| Sustaining capital | US$64M including closure (Table 22.3.1, p. 22.3); US$29M net of the US$35M plant salvage credit in the cash-flow table (Table 22.3.2, p. 22.5). The US$41M in press reports is not in the DFS tables | DFS technical report, read 2026-11-16 | [V] |
| Mine life and throughput | 13 years; 5.0 Mtpa | Same release | [V] |
| Average production | ~175 koz/yr first 5 years; ~162 koz/yr over life | DPM release, Dec 18, 2023, citing the FS | [V] |
| Fiscal terms in DFS model | 3% gross royalty (tax deductible) and 1% export levy | Osino release, June 12, 2023 | [V] |
| Technical report filed | July 13, 2023 (signed July 5, 2023; effective June 12, 2023) | Osino news release, July 13, 2023; DFS title page | [V] |
| DFS cash-flow table | Transcribed into `cases/osino_twin_hills.yaml`; reproduces NPV5 US$480M after tax (480.1) and US$742M pre-tax (743.2, cell rounding) | DFS Table 22.3.2, p. 22.5 | [V] |
| DFS internal inconsistencies | Capex timing: text says US$100M in Year -1 and US$265M in Year 0 (Section 22.2), table puts all US$365M in Year 0; the published NPV follows the table. IRR: table states 33% post-tax (reproduced), summary Table 22.4.1 and the release state 28%. Contingency labelled 15% in the table, 9.8% elsewhere (same US$34M) | DFS pp. 22.2, 22.5, 22.7 | [V] |
| Fiscal terms | Corporate tax 37.5%; 3% royalty and 1% export levy; development capital depreciated over three years; about US$75M tax losses carried forward | DFS Section 22.1, p. 22.1 | [V] |
| Permits at the DFS | Mining Licence ML238 and Environmental Clearance Certificate granted 3 November 2022 | DFS Section 4, pp. 4.3 and 4.8; Section 20 | [V] |
| Market EV at DFS | ~US$132M | Lopatnikov and Rumyantsev (2025) | [S] recompute from shares, price, cash and debt on June 12, 2023 |
| Dundee (DPM) agreement | Dec 17, 2023 (agreement date); announced Dec 18, 2023. C$0.775 cash plus 0.0801 DPM share per Osino share; implied C$1.553/share; total equity C$287M fully diluted in-the-money | DPM news release, Dec 18, 2023 | [V] |
| DPM bid in US$ | ~US$214M | Press conversion (Mining Technology, Dec 19, 2023) | [S] convert ourselves at the Dec 15, 2023 FX rate |
| Yintai (now Shanjin) agreement | Agreement Feb 23, 2024; announced Feb 25, 2024. C$1.90 cash per share; ~C$368M | Joint news release, Feb 25, 2024 | [V] |
| Yintai deal in US$ | ~US$272M | Press conversion (Mining Technology) | [S] convert ourselves at the announcement-date FX rate |
| Yintai deal closing | Aug 29, 2024 | Osino news release, Aug 29, 2024 | [V] |
| Diluted shares, net cash, debt, loan terms | Not yet extracted | Osino management information circular, March 25, 2024 (SEDAR+) | open |

Corrections to the knowledge files: the takeover was **announced** in February 2024 and **closed** on August 29, 2024. Both bids are equity prices in **Canadian dollars**; the US$214M and US$272M figures are press conversions. The US$464M NPV used by Lopatnikov and Rumyantsev (2025) does not appear in the DFS release; the release figure is US$480M post-tax. The DFS cash-flow table is the authority for reconciliation.

### 1.2 South Railroad (Nevada, gold)

| Fact | Value | Source and location | Status |
|---|---|---|---|
| Vox purchase | Announced June 7, 2021. US$1.98M cash for an effective 0.633% NSR from a private family; covers ~35% of the 1.9 Moz resource; advance minimum royalties ~C$120k/yr | Vox news release, June 7, 2021 | [V] |
| Finder's fee and capitalised cost | US$99,000 finder's fee paid to a private entity, on top of US$1.98M cash to the private individuals. Capitalised cost at Dec 31, 2021: US$2,316,757 (about US$238k above the two disclosed payments, presumably other transaction costs) | Vox audited consolidated financial statements for 2022 and 2021, Note 6 (Form 40-F exhibit 99.2, SEC, 2023) | [V] |
| Vox's own revenue estimate | ~C$250k to C$750k/yr averaged over life of mine, based on the PFS | Vox news release, June 7, 2021 | [V] |
| PFS release and report | Results Feb 18, 2020; technical report signed March 23, 2020; filed March 24, 2020 | GSV news releases; report certificate pages | [V] |
| PFS economics | Pre-tax NPV5 US$331.4M; after-tax NPV5 US$265.0M; after-tax IRR 40.0%; at US$1,400/oz Au and US$17.11/oz Ag | GSV news release, March 24, 2020 | [V] |
| PFS capital | Initial US$132.9M; life-of-mine US$285.6M | Same release | [V] |
| PFS after-tax cash flow | US$357.6M | Same release | [V] |
| PFS production | 8-year life; ~923 koz total; average **production** ~115 koz/yr. The 156 koz/yr figure is ounces **placed** on the heap, not produced | GSV releases; Vox release | [V] |
| PFS AISC | US$707/oz | Same release | [V] |
| PFS reserves | 1.246 Moz Au, 2.705 Moz Ag (P&P) | Vox release citing PFS | [V] |
| PFS gold-price sensitivity | After-tax NPV5 US$142.4M at US$1,200 to US$386.5M at US$1,600 | GSV release, sensitivity table | [V] |
| Later studies (outcome data only, ADR 0007) | FS Feb 23, 2022: initial capex US$190M, after-tax NPV5 US$315M at US$1,650/oz. Orla optimized FS Jan 2026: initial capex ~US$395M, after-tax NPV5 US$783M at US$3,100/oz | GSV material change report (SEC, 2022); Orla release Jan 2026; Equinox release Aug 17, 2026 | [V] |
| Ownership history | GSV, then Orla Mining (2022), then Equinox Gold after the Equinox-Orla combination (2026) | Equinox release, Aug 17, 2026; trade press | [V] for Equinox ownership; Orla-GSV date to confirm |
| Federal permit | BLM Record of Decision, announced Aug 17, 2026; early works started; first gold targeted 2028 | Equinox news release, Aug 17, 2026 | [V] |
| Royalty terms (ADR 0016 check) | Uncapped 0.633% NSR over parts of South Railroad; advance royalty payments "payable on an ongoing, periodic basis prior to production"; covers large portions of Dark Star, Pinion and Jasperoid Wash plus portions of the POD and Bald Mountain zones in North Railroad (outside the PFS mine plan). No buy-down right specific to this royalty is disclosed; the AIF carries only general risk language on buy-downs. Whether advance payments are credited against later royalties is not disclosed | Vox release, Feb 2025 (development update); Vox AIF, March 21, 2025; Vox asset page | [V] for what is stated; credit and buy-down remain open |
| Royalty coverage by deposit and year | Not found | Requires PFS resource and schedule by deposit (PFS Sections 14 to 16) and the royalty area map | open |

Note: the capex path (US$132.9M, then US$190M, then ~US$395M) is not a clean overrun series. Scope, cost base and price deck changed between studies.

### 1.3 Sorby Hills (Western Australia, silver-lead)

| Fact | Value | Source and location | Status |
|---|---|---|---|
| Vox agreement | Announced Sept 28, 2026. **US$**13.0M cash for an effective 0.75% uncapped NSR from a private seller; subject to FIRB; completion expected Q4 2026 | Vox news release, Sept 28, 2026 (Vox reports in US$) | [V] |
| Project status | FID Dec 2025; fully permitted; A$236M project debt (April 2026); EPC contract A$109M (May 2026); first concentrate targeted 2H 2027 | Same release | [V] |
| FEED economics | Pre-production capex A$264M; pre-tax NPV8 A$411M; IRR 37% | Knowledge file; Boab FEED release, June 2024 | [S] confirm in Boab release |

### 1.4 White Dam (South Australia, gold-copper)

| Fact | Value | Source and location | Status |
|---|---|---|---|
| Vox purchase | Agreement Sept 2, 2026; completed Sept 14, 2026. A$5.0M for a 2.0% NSR on gold and copper over nine tenements | Vox news releases, Sept 2 and Sept 14, 2026 | [V] |
| Operating status | First gold from the restart in April 2026, re-treating historic heap-leach material; fresh-ore mining restart planned 2027; target 15 to 20 koz/yr; Vertigo restart PFS and FID expected by Q1 2027 | Same releases | [V] |
| Use | Not a clean control: no reserve-based mine plan, and a July 2026 discovery adds exploration value. Kept as an example only | Decision: ADR 0008 | n/a |

## 2. Calibration sources

| Source | Figure we rely on | Status | What is still needed |
|---|---|---|---|
| Bertisen and Davis (2008), The Engineering Economist 53(2):118-139, doi:10.1080/00137910802058533 | 63 financed projects (46 completed 1995-2001 plus 17 from Castle 1985). Nominal cost ratio mean 1.25, median 1.16, SD 0.30, range 0.93 to 2.14 (Table 1, p. 122). About 14% real mean after their 0.914 inflation factor (p. 123). Shifted lognormal: shift 0.91, lognormal mean 0.35, SD 0.42 (p. 122; Equation 7, p. 134). 54% within ±15% of the size-adjusted expectation (21 of 46 outside; p. 132). Gold not statistically different (p. 129) | [V] full text read 2026-11-16 | **The abstract's "1 in 13 overrun of 100% or more" does not match the body**: Table 1 and p. 122 show 3 of 63 projects with ratios of 2.00 to 2.14 (about 1 in 21). Cite "3 of 63", not "1 in 13" |
| Suárez Nieto et al. (2024), Resources Policy 99:105427 (ScienceDirect PII S0301420724007943) | **Not an overrun sample.** The paper examines capital cost estimation in four NI 43-101 technical reports of copper projects; the ~40% figure is a warning it cites from earlier literature | [V-abs] (abstract, University of Oviedo repository) | Do not use as an overrun prior. Trace the ~40% figure to its original source if needed |
| Hatch (2016), "Statistical analysis of parameters influencing capital overruns on mining projects" | Regression on 98 projects, 1997-2015 | [P] | Candidate second overrun source; read in full |
| S&P Global Market Intelligence (Manalo 2023) | 127 mines starting 2002-2023, discovered from 1980: mean 15.7 yr discovery to production (range 6 to 32); 70 gold mines 15.2 yr | [P] verified on S&P page | Survivor sample: only mines that reached production |
| S&P (Manalo 2024) | Mean 17.9 yr for 2020-2023 starts vs 12.7 yr for 2005-2009 | [P] verified on S&P page | |
| S&P (Manalo 2025, 2026 updates) | 17.8 yr for 2020-2024 starts; 2026: 16 yr across 232 assets, ~30 yr for non-operating assets with feasibility studies | [P] verified on S&P page | Phase split (studies, decision, construction) not yet verified |
| Sykes and Trench (2014), via Lopatnikov and Rumyantsev (2025), Table 1 | Copper pyramid count ratios 88% / 82% / 14% | [V] as reported | **Cross-sectional counts, not conversion rates.** Weak prior only |
| CIM survey (Smith 2013), via Lopatnikov and Rumyantsev (2025) | Gold real discount rates: scoping 12.6%, PFS 11.1%, FS 8.9%, producing 5.7% | [V] as reported | Primary survey not yet located |
| MinEx Consulting (Schodde) | ~45% of significant discoveries became mines | [P] | Locate the primary presentation |
| McKinsey, AMC | 20% delivered within FS parameters; ~25% of FS projects fail | [P] | Locate primaries; use only as cross-checks |
| Davis (1995), "(Mis)use of Monte Carlo simulations in NPV analysis", Mining Engineering **47(1)**, January 1995, pp. 75-79 | Discounting rule | [V] citation (OneMine; Pindred's published discussion cites 47(1)) | Read in full. The knowledge files give issue 2; the correct issue is 1 |
| Iddon (2015) thesis on junior offerings | Dilution and offering discounts | open | Not yet located. The 2015 publication found is Iddon, Hettihewa and Wright, "Value relevance of accounting and other variables in the junior-mining sector", Australasian Accounting, Business and Finance Journal 9(1):25-42, doi:10.14453/aabfj.v9i1.3, which is not an offering study. The "1,526 offerings" claim is unverified |

**Stage-transition priors.** No cohort-based source (one that follows projects from a study stage to a build decision) has been found. Searches so far returned the cross-sectional Sykes and Trench counts and unsourced aggregator figures, which are excluded. Until a cohort source is found, stage priors are wide and flagged, and the flag is carried into the waterfall.

## 3. Excluded sources

| Source | Reason |
|---|---|
| Discovery Alert, Farmonaut and similar aggregators (for example "60% of FS projects achieve financing") | No traceable primary source [X] |
| ResearchGate "20-60% overrun review" | Low quality [X] |
