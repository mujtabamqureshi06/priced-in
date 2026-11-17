# Phase 4 panel protocol

- Status: draft. It freezes when the open checks in section 8 are closed and this line changes to "frozen"; the freezing commit hash is then recorded in section 9. No outcome data is collected before then.
- Decision records: ADR 0051, amended by ADRs 0052 and 0053.

## 1. Question

Do the build odds implied by a gold developer's market value carry information about whether its project reaches a construction decision within 36 months, beyond what price to net asset value (P/NAV) and study stage already carry?

The test is descriptive. A positive result would not show that prices are right or wrong, and the project makes no claim about trading.

## 2. Universe

**Panel.** Gold development projects whose owner was listed on the ASX, the TSX or the TSXV, pooled in one panel (ADR 0053). Canadian filings for issuers no longer active remain public through SEDAR+ and its archive of legacy SEDAR filings, so TSX and TSXV names do not select on survival the way company-website archives would.

**Entry rule.** A project enters at the first economic study (scoping study or preliminary economic assessment (PEA), pre-feasibility study (PFS) or feasibility study (FS)) that its listed owner published between January 1, 2012 and December 31, 2021 and that reports an after-tax NPV and IRR. A study that reports pre-tax figures only does not open an entry; the project may enter at a later study in the window that does. Studies published before 2012, by the same or an earlier owner, do not exclude the project. They are recorded as covariates: the number of earlier studies and the years since the project's first study. A project enters once. If it is sold, it is followed under its new owner and does not re-enter. The 36-month outcome window closes by December 31, 2024.

**Candidate list.** Built before any outcome is examined, from two named sources (section 8 item 2): a company screen that includes delisted, acquired and wound-up companies, and, for ASX developers the screen missed, the government's major-projects lists. Inclusion is decided only from documents dated on or before the entry study. Every candidate dropped later, for example for missing documents, is recorded with its reason, and drop rates are reported by outcome.

**Exclusions, judged at the entry study's date.**
- The owner had more than one project at study stage. Projects at pure exploration stage do not count.
- The owner was producing: commercial production, or trial, test or bulk-sample mining at any mine it owned.
- The owner held less than 50% of the project. An earn-in toward a stake does not count as holding it.
- By-product revenue (silver, copper and others together) above 20% of study revenue.
- Royalty and streaming companies, and projects that are not metal mines.

## 3. Snapshots

Quarterly, at each calendar quarter end from the first study date until the earliest of:
- a construction decision;
- a takeover completion;
- 36 months after the first study.

At each snapshot the panel records:
- **Share price:** the closing price, as traded, from the source named in section 8.
- **Share counts:** shares on issue, options and warrants by series, from the latest quarterly Appendix 5B or periodic report published before the snapshot.
- **Balance sheet:** cash and debt from the same report.
- **Study:** the latest study published before the snapshot (stage, after-tax NPV and rate, IRR, initial capital, life, annual production, all-in sustaining cost, price deck, tax basis, document and page).
- **Market inputs:** gold spot, the real rate and AUD/USD on the snapshot date (ADR 0024 conventions).

No information dated after a snapshot enters that snapshot.

## 4. Outcomes

For each project, with the date and source document:
- **Event:** a construction decision, defined as a board decision to proceed with construction, publicly announced, with funding committed or in place.
- **Competing outcome:** completion of a takeover of the company or a sale of the project. If the project is sold, it is followed under its new owner, and a construction decision by that owner within the window counts as the event.
- **Observed non-event:** no construction decision by the end of the window, including abandonment, impairment to nil or a change of business. Abandonment is not censoring; coding it as censored would bias the test toward success.
- **Censored:** only when the project cannot be tracked after a stated search (company announcements, the acquirer's disclosures, news).

The labelling form, field definitions and search procedure are in `docs/phase4/labelling.md`. A random 20% of outcome labels are coded a second time from the source documents, blind to the first coding. Disagreements are reported and resolved by a stated rule.

**Financings.** Each equity raise in the window is recorded with its price, the closing price before announcement, and any attached warrants. That sample replaces or confirms the 10.54% issue-discount prior (ADR 0030, #94).

## 5. Implied odds per snapshot

**Mine plan.** A parametric study builder turns each study's headline figures into an annual cash-flow schedule, calibrated so that it reproduces the study's reported after-tax NPV and IRR.

**Validation.** A subsample is drawn at random with a recorded seed: the larger of 10 projects or 20% of the panel. Each project in it has its study cash-flow table hand-transcribed with the existing case template. The builder's error against the transcription (in project value at the snapshot's market inputs) is reported, and that tolerance is carried into every result. The existing four cases are not used for validation; three of them are not ASX gold.

**Implemented.** `pricedin.parametric` builds the schedule: initial capital over the pre-production years, a production profile tilted by one parameter with the life-of-mine total fixed, operating cost as a calibrated factor times all-in sustaining cost, and tax at the marginal rate after straight-line depreciation. The cost factor and tilt are solved to match the study's after-tax NPV and IRR. As an informative check only, the builder applied to Osino's DFS headline figures gives project values within 0.6% of the hand-transcribed case at market prices and spreads of 0%, 5% and 10%. This is not the validation set.

**Inversion.** The existing developer adapter and inversion read the equity claim at each snapshot (ADRs 0030, 0031, 0047). Results are reported at the break-even spread and at stated reference spreads, with the timing prior stated (ADR 0023).

## 6. Test

- **Primary:** discrimination of the event within 36 months by the zero-delay implied odds at the first snapshot after each study, measured by AUC with a confidence interval, and calibration by Brier score.
- **Comparators:** P/NAV at the same snapshot (price over the study's after-tax NPV) and study-stage indicators.
- **Model:** logit of the event on implied odds, with P/NAV and stage as controls. Takeover is treated as a competing outcome (Fine and Gray subdistribution hazard as a robustness check).
- **Clustering:** quarterly snapshots of one project are not independent, so standard errors are clustered by project, and the primary test uses one snapshot per project.
- **Covariates:** an exchange indicator (ASX against TSX and TSXV), the number of studies before entry and the years since the project's first study.
- **Checks specified now, before any outcome is labelled (ADR 0053):**
  - ASX projects only, and TSX and TSXV projects only.
  - Projects whose first economic study by any owner falls in the window (the strict entry rule).
  - With and without the candidates added from the government lists.
  - The number of projects that entered later than their first in-window study because that study reported pre-tax figures only, by exchange and stage.
- **Selection:** the candidate screen's recall is reported by outcome (section 8 item 2). If recall differs between built and unbuilt projects by more than about 20 percentage points in any reported variant of the audit, results are shown adjusted for selection, or presented as descriptive only.

## 7. Power

With one snapshot per project and a two-sided 5% test at 80% power, the smallest AUC distinguishable from 0.5 (Hanley and McNeil 1982 standard errors) is:

| Projects | Event share | Events | Detectable AUC |
|---|---|---|---|
| 40 | 30% | 12 | 0.78 |
| 50 | 30% | 15 | 0.75 |
| 50 | 40% | 20 | 0.73 |
| 60 | 40% | 24 | 0.71 |

A comparison of implied odds against P/NAV needs a difference in AUC, which these sizes cannot detect reliably unless the difference is large. The paper reports that difference with its interval and does not call it significant unless it is. If the core panel falls below 30 projects, the design goes back for review.

## 8. Open checks before freezing

1. **Share prices and shares outstanding (source chosen).** S&P Capital IQ through the University of Toronto's academic licence. It covers listed and delisted ASX and TSX/TSXV companies.
   - S&P's academic licence permits publishing derived results, such as implied probabilities and test statistics, provided the underlying data cannot be reconstructed from them. Raw prices and share counts are never committed; the repository holds identifiers, dates, derived values and the extraction steps. Readers without Capital IQ cannot fully reproduce the panel, and the paper says so and credits S&P.
   - S&P's terms prohibit automated access to authenticated content, including access by AI agents. All exports are therefore run by the licensed user, by hand or through S&P's own Excel plug-in. No browser automation is used.
   - Market Index is ruled out: its snapshots are for personal use only, its terms forbid robot access and scraping, and reuse needs its written consent. The free end-of-day archive is ruled out for the reasons recorded in #110.
2. **Candidate list (built 2026-11-17; to be frozen).** The licence does not include a usable property database, so the list is built from a company screen in S&P Capital IQ Pro, run by hand by the licensed user on 2026-11-17.
   - **Frame:** Primary Industry = Gold; every company status (operating, acquired, out of business, liquidating and others); Exchange [Current & Historical] in TSX, TSXV and ASX. 1,240 companies, of which 1,003 reported at some point in 2012 to 2021 or have no report date. Two lessons from building it are recorded so the screen can be repeated: the older "Gold Ores" industry code misses most listed parent companies, and "Exchange [Historical]" alone returns only companies that have since left those exchanges.
   - **Study flags:** two further screens on the same frame flag companies whose Key Development headlines dated 2012 to 2021 contain "feasibility", "preliminary economic assessment" or "scoping study" (246 companies), or "study", "NPV" or "reserve" (254); 301 in total. Business descriptions that mention a study add further candidates.
   - **Review:** 443 candidates were coded IN, CHECK or OUT, each with a recorded reason. CHECK cases are resolved only from documents dated on or before the study. Exclusions were re-checked on a random 10% sample (27 of 268, seed 20261117) by the same analyst, with 27 upheld; that is a self-check and is reported as one. An independent blind check of the same 27 exclusions and a random 10% of inclusions, by a reviewer given only the rules and public sources, must be completed and every disagreement resolved under these rules before the list is frozen.
   - **Recall audit (ASX).** The screen's recall is checked against the government's major-projects gold lists for 2017 to 2021. "Built" is a crude proxy: a committed or completed status in those lists by 2021. The order of events was: a first count on an ad hoc list of names; then a written definition of the audit set, every ASX-listed company in the lists whose project was a new or redeveloped mine and that was not producing when first listed, with renamed companies counted once (Spitfire Materials became Bardoc Gold); then a second count. All three counts are reported.

     | Audit set | Companies | Caught | Built: caught | Not built: caught | Gap |
     |---|---|---|---|---|---|
     | Ad hoc list (first count) | 23 | 16 | 6 of 8 | 10 of 15 | about 8 points |
     | Defined set (headline) | 20 | 15 | 5 of 6 | 10 of 14 | about 12 points |
     | Defined set plus two expansion projects of producing companies (Blackham, Citigold) | 22 | 17 | 7 of 8 | 10 of 14 | about 16 points |

     The 20-point threshold in section 6 is judged against the least favourable variant, not the headline; all three are below it. With six to eight built projects, one project moves the built rate by 12 to 17 points, so none of these gaps is distinguishable from zero. The audit is a check, not an estimate. Missed: Calidus, Barton and Medallion (in the frame without a study flag), and Kin Mining and Explaurum (not in the frame).
   - **Second source:** government-listed ASX developers the screen missed are added by name, and results are reported with and without them. Of the five misses, Calidus, Kin Mining and Explaurum are candidates; Barton's and Medallion's first studies were published after 2021.
   - **TSX and TSXV recall: unmeasured.** One attempt was made, with Natural Resources Canada's Major Projects Inventory. Its published reports for the window give provincial totals, not a project-level list, and its project-level open data covers only projects active today, which would select on the outcome. No other free independent list was found, so the paper states that TSX and TSXV recall is unmeasured.
   - At least 20% of construction-decision dates are verified against company announcements.

3. **Government major-projects lists (checked).** The Australian Government's Resources and Energy Major Projects reports: an annual census of resources and energy projects worth over A$50 million, published with a project-level data file under a Creative Commons licence. Data files exist for the 2017 to 2021 editions (`data/phase4/remp_gold.csv`); an April 2015 list is archived on data.gov.au; none was found for 2012 to 2014. They serve as the recall audit and the second source in item 2, not as the frame.

## 9. Freeze

Freezing commit: not yet frozen.
