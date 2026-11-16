# Sources register

Every source that feeds a prior or a test case, with its verification status and where the figure sits. Third-party documents are not stored in this repository (ADR 0003).

Status: **[V]** verified against the primary document or the issuer's own release. **[V-abs]** verified from the abstract or citation only; the full text is still needed for the specific figure. **[S]** seen only in a secondary summary; do not cite publicly. **[P]** practitioner or industry source, not peer-reviewed. **[J]** a stated judgment, recorded in a decision record and flagged in every output. **[X]** do not use.

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

Corrections to figures often reported elsewhere: the takeover was **announced** in February 2024 and **closed** on August 29, 2024. Both bids are equity prices in **Canadian dollars**; the US$214M and US$272M figures are press conversions. The US$464M NPV used by Lopatnikov and Rumyantsev (2025) does not appear in the DFS release; the release figure is US$480M post-tax. The DFS cash-flow table is the authority for reconciliation.

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
| Ownership history | GSV, then Orla Mining (2022), then Equinox Gold after the Equinox-Orla combination (2026) | Equinox release, Aug 17, 2026; trade press | [V]; Orla acquisition closed August 12, 2022 (section 1.5) |
| Federal permit | BLM Record of Decision, announced Aug 17, 2026; early works started; first gold targeted 2028 | Equinox news release, Aug 17, 2026 | [V] |
| Royalty terms (ADR 0016 check) | Uncapped 0.633% NSR over parts of South Railroad; advance royalty payments "payable on an ongoing, periodic basis prior to production"; covers large portions of Dark Star, Pinion and Jasperoid Wash plus portions of the POD and Bald Mountain zones in North Railroad (outside the PFS mine plan). No buy-down right specific to this royalty is disclosed; the AIF carries only general risk language on buy-downs. Whether advance payments are credited against later royalties is not disclosed | Vox release, Feb 2025 (development update); Vox AIF, March 21, 2025; Vox asset page | [V] for what is stated; credit and buy-down remain open |
| Royalty coverage by deposit and year | Not found | Requires PFS resource and schedule by deposit (PFS Sections 14 to 16) and the royalty area map | open |

Note: the capex path (US$132.9M, then US$190M, then ~US$395M) is not a clean overrun series. Scope, cost base and price deck changed between studies.

### 1.3 Sorby Hills (Western Australia, silver-lead)

| Fact | Value | Source and location | Status |
|---|---|---|---|
| Vox agreement | Announced Sept 28, 2026. **US$**13.0M cash for an effective 0.75% uncapped NSR from a private seller; subject to FIRB; completion expected Q4 2026 | Vox news release, Sept 28, 2026 (Vox reports in US$) | [V] |
| Project status | FID Dec 2025; fully permitted; A$236M project debt (April 2026); EPC contract A$109M (May 2026); first concentrate targeted 2H 2027 | Same release | [V] |
| FEED economics | Pre-production capex A$264M; pre-tax NPV8 A$411M; IRR 37%; pre-tax only, no after-tax figures | Boab FEED release, June 6, 2024, Tables 8 to 10, pp. 12 to 14 | [V] |
| FEED schedule and deck | Annual lead and silver revenue, TC, RC, logistics, costs, capex (Table 10, p. 14); deck by financial year (Table 7, p. 12); payable 17.2 Moz silver and 546 kt lead (Table A11, p. 40) | Same release; transcribed in `cases/sorby_hills.yaml` | [V] |
| FEED still applies | Production targets and financial forecasts "continue to apply" after the plant change | Boab ASX release, Dec 10, 2025, compliance statement | [V] |
| Underlying royalty | 1% net smelter royalty to Quintana MH Holding Company LLC from the original acquisition, classed as a contingent liability; metals and interest not stated | Boab half-year report to Dec 31, 2025, Note 14, p. 21 | [V] |
| Market on Sept 28, 2026 | Silver US$60.81/oz; LME lead cash US$1,886/t, 3-month US$1,911.5/t; 10-year TIPS 2.90%; 3-month bill 4.28%; US$0.7020 per A$ | `data/snapshots/2026-09-28.yaml` | [V] FRED; [P] vendor and secondary prices |

### 1.4 White Dam (South Australia, gold-copper)

| Fact | Value | Source and location | Status |
|---|---|---|---|
| Vox purchase | Agreement Sept 2, 2026; completed Sept 14, 2026. A$5.0M for a 2.0% NSR on gold and copper over nine tenements | Vox news releases, Sept 2 and Sept 14, 2026 | [V] |
| Operating status | First gold from the restart in April 2026, re-treating historic heap-leach material; fresh-ore mining restart planned 2027; target 15 to 20 koz/yr; Vertigo restart PFS and FID expected by Q1 2027 | Same releases | [V] |
| Use | Not a clean control: no reserve-based mine plan, and a July 2026 discovery adds exploration value. Kept as an example only | Decision: ADR 0008 | n/a |

### 1.5 Gold Standard Ventures takeover by Orla Mining (2022)

| Fact | Value | Source and location | Status |
|---|---|---|---|
| Terms | 0.1193 Orla share plus C$0.0001 per Gold Standard share; C$0.655 per share and C$242M gross at the June 10, 2022 close; 35% premium to the close and to the 10-day VWAP | Joint news release, June 13, 2022 | [V] |
| Dates | Arrangement agreement June 12, 2022; announced June 13; closed August 12, 2022 | Management information circular, July 6, 2022 (SEC 6-K, exhibit 99.2); closing release, Aug 12, 2022 | [V] |
| Securities | 358,735,368 shares, 15,724,678 options and 4,245,580 RSUs at the June 30, 2022 record date | Circular, Q&A | [V] |
| Balance sheet, March 31, 2022 | Cash C$17,491,368; lease liabilities C$363,770; no borrowings; deferred revenue C$2,880,535 (Orion silver stream deposit); 18,397,523 options at a C$1.08 weighted average, of which 4,833,410 granted at C$0.57 in Q1 2022 | Interim statements, three months ended March 31, 2022 (SEC 6-K, May 9, 2022, exhibit 99.1) | [V] |
| Silver stream | Orion, October 29, 2020: all silver from the South Railroad mine delivered for 15% of the spot price; US$2M deposit | Same statements, Note 6 | [V] |
| 2022 FS | Report dated March 14, 2022 (effective Feb 23, 2022). After-tax NPV5 US$314.8M, NPV10 US$247.6M, IRR 44.3% at US$1,650/oz Au and US$21.50/oz Ag; initial capital US$190.2M; mid-year discounting (Section 22.14) | FS Tables 22-5 to 22-7 (SEC 6-K, March 2022, exhibit 99.1) | [V] |
| Company schedule | Notice of Intent expected in Q1 2022; construction from Q2 2023 over 12 months; first gold Q3 2024 | Gold Standard news release, Feb 23, 2022 | [V] |
| Notice of Intent (outcome data only) | Published in the Federal Register in August 2025 (FR Doc. 2025-15310) | Federal Register | [V] |
| Orla balance sheet, June 30, 2022 | Cash US$66.7M; credit facility US$129.2M; Fresnillo obligation US$37.8M; leases US$1.3M; 258.478M shares; 7.82M options at C$2.53; warrants 3.0M at C$1.40 and 29.545M at C$3.00; 0.44M RSUs and 0.66M DSUs; G&A US$5.83M for six months | Orla interim statements, six months ended June 30, 2022 (SEC 6-K, August 2022, exhibit 99.1) | [V] |
| Shares issued at closing | 43,688,556 Orla shares, fair value US$149.363M (US$3.4188 a share) | Orla interim statements, nine months ended September 30, 2022, note 12 | [V] |
| Camino Rojo FS (January 2021) | After-tax NPV5 US$452M at US$1,600/oz; annual cash-flow table pp. 22-13 to 22-14 | Kappes, Cassiday & Associates technical report (SEC 6-K, February 2021, exhibit 99.1) | [V] |
| Cerro Quema PFS (July 2021) | After-tax NPV5 US$176M at US$1,600/oz; US$79M to US$272M from US$1,250 to US$1,950 | Orla material change report, July 28, 2021 | [V] |

## 2. Calibration sources

| Source | Figure we rely on | Status | What is still needed |
|---|---|---|---|
| Bertisen and Davis (2008), The Engineering Economist 53(2):118-139, doi:10.1080/00137910802058533 | 63 financed projects (46 completed 1995-2001 plus 17 from Castle 1985). Nominal cost ratio mean 1.25, median 1.16, SD 0.30, range 0.93 to 2.14 (Table 1, p. 122). About 14% real mean after their 0.914 inflation factor (p. 123). Shifted lognormal: shift 0.91, lognormal mean 0.35, SD 0.42 (p. 122; Equation 7, p. 134). 54% within ±15% of the size-adjusted expectation (21 of 46 outside; p. 132). Gold not statistically different (p. 129) | [V] full text read 2026-11-16 | **The abstract's "1 in 13 overrun of 100% or more" does not match the body**: Table 1 and p. 122 show 3 of 63 projects with ratios of 2.00 to 2.14 (about 1 in 21). Cite "3 of 63", not "1 in 13" |
| Suárez Nieto et al. (2024), Resources Policy 99:105427 (ScienceDirect PII S0301420724007943) | **Not an overrun sample.** The paper examines capital cost estimation in four NI 43-101 technical reports of copper projects; the ~40% figure is a warning it cites from earlier literature | [V-abs] (abstract, University of Oviedo repository) | Do not use as an overrun prior. Trace the ~40% figure to its original source if needed |
| Hatch (2016), "Statistical analysis of parameters influencing capital overruns on mining projects" | Regression on 98 projects, 1997-2015 | [P] | Candidate second overrun source; read in full |
| S&P Global Market Intelligence (Manalo 2023) | 127 mines starting 2002-2023, discovered from 1980: mean 15.7 yr discovery to production (range 6 to 32); 70 gold mines 15.2 yr | [P] verified on S&P page | Survivor sample: only mines that reached production |
| S&P (Manalo 2024) | Mean 17.9 yr for 2020-2023 starts vs 12.7 yr for 2005-2009 | [P] verified on S&P page | |
| S&P (Manalo 2025, 2026 updates) | 17.8 yr for 2020-2024 starts; 2026: 16 yr across 232 assets, ~30 yr for non-operating assets with feasibility studies | [P] verified on S&P page | Phase split (studies, decision, construction) not yet verified |
| Council on Environmental Quality (June 12, 2020), Environmental Impact Statement Timelines (2010-2018), https://nepa.gov/sites/default/files/documents/CEQ_EIS_Timeline_Report_2020-6-12.pdf | BLM, 143 EISs: mean NOI to ROD 4.36 yr (Figure 5, p. 9), median 3.79 yr (Figure 6, p. 13); all agencies mean 4.5, median 3.5, quartiles 2.2 and 6.0 (p. 1, Figure 1 p. 4) | [V] | Covers all EIS types, not mines only. Used for South Railroad base timing (ADR 0023) |
| Sykes and Trench (2014), via Lopatnikov and Rumyantsev (2025), Table 1 | Copper pyramid count ratios 88% / 82% / 14% | [V] as reported | **Cross-sectional counts, not conversion rates.** Weak prior only |
| CIM survey (Smith 2013), via Lopatnikov and Rumyantsev (2025) | Gold real discount rates: scoping 12.6%, PFS 11.1%, FS 8.9%, producing 5.7% | [V] as reported | Primary survey not yet located |
| McNulty (1998), "Developing innovative technology", Mining Engineering 50(10):50-55 | Four ramp-up curves (Fig. 1, p. 52) from 41 plants; classification 23/5/6/7 by series (Table 2, p. 53); hydrometallurgical oxide plants, including heap leach, 6/1/0/0 | [V] full text read 2026-11-16 (scan supplied by the owner) | Curves digitised by eye, about ±2 points |
| MinEx Consulting (Schodde) | ~45% of significant discoveries became mines | [P] | Locate the primary presentation |
| McKinsey, AMC | 20% delivered within FS parameters; ~25% of FS projects fail | [P] | Locate primaries; use only as cross-checks |
| Davis (1995), "(Mis)use of Monte Carlo simulations in NPV analysis", Mining Engineering **47(1)**, January 1995, pp. 75-79 | Discounting rule | [V] citation (OneMine; Pindred's published discussion cites 47(1)) | Read in full. Some secondary sources give issue 2; the correct issue is 1 |
| Iddon (2015) thesis on junior offerings | Dilution and offering discounts | open | Not yet located. The 2015 publication found is Iddon, Hettihewa and Wright, "Value relevance of accounting and other variables in the junior-mining sector", Australasian Accounting, Business and Finance Journal 9(1):25-42, doi:10.14453/aabfj.v9i1.3, which is not an offering study. The "1,526 offerings" claim is unverified |

**Stage-transition priors.** No cohort-based source (one that follows projects from a study stage to a build decision) has been found. Searches so far returned the cross-sectional Sykes and Trench counts and unsourced aggregator figures, which are excluded. Until a cohort source is found, stage priors are wide and flagged, and the flag is carried into the waterfall.

## 3. Excluded sources

| Source | Reason |
|---|---|
| Discovery Alert, Farmonaut and similar aggregators (for example "60% of FS projects achieve financing") | No traceable primary source [X] |
| ResearchGate "20-60% overrun review" | Low quality [X] |

## Producing-royalty controls and reference rates (ADRs 0026 to 0028)

| Source | Figure | Status | Use |
|---|---|---|---|
| Metalla news release, June 22, 2020; audited statements, seven months to Dec 31, 2020, Notes 4(a), 13(b) | Wharf 1.0% GVR: US$1.0M cash, 899,201 shares at US$5.52 (US$4,964,152), costs US$149,102 | [V] | Wharf control price |
| Coeur news release, Feb 18, 2020; 2019 10-K reserves table; Q2 2020 10-Q | Wharf YE2019 P&P 768 koz contained, 79% recovery; 2020 guidance 80 to 90 koz | [V] | Wharf Tier 2 schedule |
| Metalla Wharf royalty page | Metalla estimates 100% of Wharf reserves and resources are subject to the royalty | [P] | Coverage check |
| Osisko Gold Royalties, audited 2020 statements, Notes 19 and 26 | Post-tax real discount rate 3.5% (2020), 4.1% (2019) for the Éléonore and Canadian Malartic NSR CGUs; recoverable amount on fair value less costs of disposal; long-term gold US$1,600 (2020); statutory rate 26.5% | [V] | Convention reference, applied with its own gold deck (ADRs 0028, 0045) |
| Osisko, audited 2021 statements, Note 17 | 4.3% (2021) | [V] | Sensitivity only (published after the South Railroad date) |
| Sandstorm release Dec 18, 2017; Acacia RNS Jan 17, 2018 | Houndé 2% NSR, US$45M cash; covers Kari North and South, nearly all of the 2.1 Moz reserve | [V] | Candidate control; not qualified: no pre-deal annual schedule by deposit found in free sources |
| Franco-Nevada, audited 2020 statements, Note 8 | Discount rates disclosed only for energy CGUs (5% to 12%) | [V] | Not comparable to gold royalties |
| Gold Royalty 6-K, Jul 31, 2023; Endeavour Silver release, Jul 31, 2023 | Cozamin 1.0% NSR on Calicanto and Vicochea concessions, US$7.5M cash | [V] | Candidate; concession-level production not disclosed |
| TMAC releases 2019 to 2020; Osler deal note | Hope Bay additional 1.5% NSR, US$40M (Maverix, 2019) | [V] | Excluded: out-of-date plan, under three years of production |
| Council on Environmental Quality, June 2020 | See section on timing | [V] | ADR 0023 |
| OR Royalties (formerly Osisko), audited statements for 2025 (Form 40-F exhibit 99.2, filed Feb 2026), Note 12 | Post-tax real discount rate 5.1% (2025), 4.9% (2024), goodwill test on fair value less costs of disposal; long-term gold US$3,327 and silver US$42 (2025), US$2,184 and US$27 (2024); statutory tax rate 26.5% | [V] | Reference rate for deals dated after Feb 2026, applied with its own silver deck (ADRs 0035, 0045) |

## Method benchmarks

| Source | Figure | Status | Use |
|---|---|---|---|
| Samis, Davis and Laughton (2007), Project Evaluation Conference, Melbourne, AusIMM, pp. 127 to 137 | Real-options practice risk-adjusts the uncertain inputs and discounts the resulting cash flows with risk-free factors; each claimant's cash flow is discounted for its own risk; contrasted with discounting net cash flow at one constant rate (pp. 128 to 129) | [V] read in full | Discounting rule (methodology section 7, ADR 0012) |
| Brennan and Schwartz (1985), "Evaluating Natural Resource Investments", Journal of Business 58(2), 135-157, Table 1 (p. 148) and Table 2 (p. 149) | Copper mine parameters; values of the open and closed mine at US$0.30 to US$1.00/lb; critical prices (p. 148) | [V] | ADR 0040 |
| Maier (2021), "Re-evaluating natural resource investments under uncertainty: An alternative to limited traditional approaches", Annals of Operations Research 299(1), 907-937, doi:10.1007/s10479-020-03569-w (open access), Sect. 2.2, Tables 1 and 2 | Discrete-time specification of the Brennan and Schwartz mine; same values reproduced | [V] | ADR 0040 |
| Longstaff and Schwartz (2001), Review of Financial Studies 14(1), 113-147 | Least-squares Monte Carlo method | [V] citation | ADR 0037 |
| QuantLib 1.44, `FdBlackScholesVanillaEngine` | American put reference value 4.487 (S=36, K=40, r=6%, vol 20%, 1 year) | [V] computed | ADR 0037 |
| Fuller (2023), "An option-value framework for valuing mining streams", Resources Policy, doi:10.1016/j.resourpol.2023.103847 | A stream as a portfolio of European calls | [P] abstract read | ADR 0041 |

## Osino company documents (archived company website)

| Source | Figure | Status | Use |
|---|---|---|---|
| Osino condensed interim financial statements, September 30, 2023 (osinoresources.com/wp-content/uploads/2023/12/Financial-Statements-Osino-September-2023-.pdf) | Cash C$8,338,550 (Note 7); credit facility C$19,676,192 (Note 12); leases C$83,804 (Note 11); other financial liabilities C$2,668,149 (Note 10); 159,514,399 shares; 9,431,134 options at C$1.02; 9,251,940 warrants (Note 8): 4,772,727 at C$1.35, 2,061,524 at C$0.88, 1,233,737 at C$1.46, 1,183,952 at C$1.53 (C$1.28 weighted average; Note 12 gives the Nebari strikes in US$); 2,911,618 RSUs and 110,672 DSUs (Note 8) | [V] | Net debt and dilutive securities (ADRs 0033, 0048) |
| Osino condensed interim financial statements, March 31, 2023 (osinoresources.com/wp-content/uploads/2023/05/ORC-March23-FINAL.pdf) | Cash C$8,822,349; Nebari facility C$5,977,670 and accrued interest C$288,059 (Note 12); lease liabilities C$111,939; other financial liabilities C$124,546; 158,201,765 shares; 10,710,235 options at C$0.94 (p. 17); warrants 4,772,727 at C$1.35, 572,727 at C$1.10, 2,061,524 at US$0.88 as labelled (C$0.88; p. 18); 2,675,195 RSUs (p. 18). Subsequent events (Note 17): 38,636 broker warrants exercised at C$1.10 on April 17, 2023; Nebari second tranche of US$5M less a US$50,000 fee, with 1,233,737 warrants at US$1.08 (C$1.45) | [V] | July 2023 reading (ADR 0048) |
| Osino MD&A, Q1 2023, dated May 29, 2023 (osinoresources.com/wp-content/uploads/2023/05/MD-and-A-Analysis-1Q2023-FINAL.pdf) | Corporate G&A C$1,724,844 for the quarter (p. 17); second Nebari tranche drawn and about C$10.9M of cash at the report date (p. 15) | [V] | G&A and cash-spent sensitivity (ADR 0048) |
| Osino management information circular, trading price table (p. 109) | July 2023 trading range C$1.07 to C$1.20 per share | [P] page to re-check against the filed circular | July 2023 price band (ADR 0048) |
| Osino MD&A, Q3 2023, dated November 29, 2023 | Corporate G&A C$5,448,933 for nine months (p. 14); FEED by 1Q2024; construction start 1H2024; potential first gold 1Q2026 | [V] | G&A and timing (ADRs 0031, 0033) |
| Osino management information circular, January 29, 2024 (Dundee arrangement), Appendices C and D | Fairness opinions dated December 17, 2023; Eight Capital Twin Hills discount rates 10.5% to 13.5%, US$1,850 gold, P/NAV 0.25x to 0.50x (comparables), 0.35x to 0.60x (precedents) | [V] | Reference band (ADR 0033) |
| DPM news release, December 18, 2023 | C$0.775 cash plus 0.0801 DPM share; C$1.553 per share; C$287 million fully diluted in the money; 37.2% premium to the December 15 close | [V] | Dundee price and undisturbed price |
| Yintai (Shanjin) news release, February 25, 2024 | C$1.90 per share in cash, about C$368 million | [V] | Shanjin price |
