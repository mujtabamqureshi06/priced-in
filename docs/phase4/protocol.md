# Phase 4 panel protocol

- Status: draft. It freezes when the two open checks in section 8 are closed and this line changes to "frozen"; the freezing commit hash is then recorded in section 9. No outcome data is collected before then.
- Decision record: ADR 0051.

## 1. Question

Do the build odds implied by a gold developer's market value carry information about whether its project reaches a construction decision within 36 months, beyond what price to net asset value (P/NAV) and study stage already carry?

The test is descriptive. A positive result would not show that prices are right or wrong, and the project makes no claim about trading.

## 2. Universe

**Core panel.** The candidate route in section 8 item 2 may widen this to TSX and TSXV owners (ADR 0052). As first designed: ASX-listed companies whose main asset is a single gold project, and that published a first scoping study (PEA), pre-feasibility study (PFS) or feasibility study (FS) between January 1, 2012 and December 31, 2021. The 36-month outcome window then closes by December 31, 2024.

**Candidate list.** The list is built from a stated, complete source that includes companies later delisted, acquired or wound up, before any documents are checked. The source is an open check (section 8). Inclusion is decided from the candidate list alone. Every candidate dropped later, for example for missing documents, is recorded with its reason, and drop rates are reported by outcome.

**Supplementary set.** TSX and TSXV gold developers whose own websites archive their filings (as Osino's did) are kept in a separate, labelled set. Archives survive mainly for companies that survived, so these names would select on the outcome and do not enter the core test.

**Exclusions, decided before outcomes are seen.**
- Companies with more than one project at study stage at the snapshot date.
- Projects whose study does not report an after-tax NPV and IRR.
- Byproduct credits above 20% of study revenue.

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

A random 20% of outcome labels are coded a second time from the source documents, blind to the first coding. Disagreements are reported and resolved by a stated rule.

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
2. **Candidate list: route depends on the property database.** The REMP data files exist for the 2017 to 2021 editions only (the December 2016 report has no project list; an April 2015 list is archived on data.gov.au; none was found for 2012 to 2014). They give 32 gold projects at the feasibility stage, but only about 16 ASX-listed single-project developers, below the 30-project floor.
   - **Preferred:** a screen of S&P's mining property database, if the licence includes it. The screen covers gold properties whose stage reached scoping, PFS or FS between 2012 and 2021, with ASX, TSX or TSXV owners, inactive properties included. Its criteria and run date are recorded here, and the inclusion list is frozen before any outcome is examined. Stage dates are checked on a sample against company announcements, so they are known to have been recorded at the time. With a complete third-party list, TSX and TSXV names enter the core panel. Each snapshot uses the study in force on its date.
   - **Fallback:** the REMP frame (2015 and 2017 to 2021 lists), ASX only, run as a pilot case series. No significance test is claimed.
   - Either way, at least 20% of construction-decision dates are verified against company announcements.

3. **REMP frame (checked).** The Australian Government's Resources and Energy Major Projects reports. They form an annual census of resources and energy projects worth over A$50 million, published with a project-level data file under a Creative Commons licence. Earlier editions (BREE, 2012 and 2013) were twice yearly.
   - The core panel takes every gold project listed at the feasibility stage in any edition from 2012 to 2021, including projects later removed from the list.
   - Two consequences become inclusion rules: projects below A$50 million in capital are outside the core panel, and the 2023 change from "feasibility" to "advanced feasibility" does not affect the 2012 to 2021 entry window.
   - Each edition used is recorded with its URL and retrieval date.

## 9. Freeze

Freezing commit: not yet frozen.
