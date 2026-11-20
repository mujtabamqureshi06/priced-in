# Phase 5 protocol: probability and timing of a construction decision by study stage

Status: fixed before the frame is counted and before any new outcome is labelled (ADR 0064; frame sources amended by ADR 0065 before the frame was counted). Outcomes for the Phase 4 panel are already known. That is acceptable here because the table is a count by stage with no fitted parameters, and the rules below are fixed first.

## 1. Question

A gold project held by a company with no producing mine has just reached a given study stage. How likely is a construction decision, by any owner, within 12, 24, 36 and 60 months? How likely is a takeover of its owner over the same periods?

The deliverable is the full-period table with 95% intervals. Section 7 adds a stability test across two periods.

## 2. Frame

The table needs no prices. The Phase 4 exclusions that existed only for the price test therefore do not apply: after-tax figures, market data, one asset per company, and listing at a snapshot.

1. **Sources.** These are combined and de-duplicated by the project-identity rule (Phase 4 protocol section 2, interpretation 4):
   - the Phase 4 candidate list (`data/phase4/candidates.csv`, study dates 2012 to 2021);
   - the stock-sample screen (ADR 0062, study dates 2017 to 2022);
   - a full-text screen of Capital IQ key developments dated 2008 to 2022, selecting items whose description (not only the headline) quotes an NPV, an IRR or after-tax figures (ADR 0065). Every company it flags is checked, inside or outside the Phase 4 company frame, including listed parents that Capital IQ does not classify as gold companies. The holder must be listed on the ASX, TSX or TSXV at the study date, as for the other two sources. Inclusion is decided from documents dated on or before each study, by a coder who is not given outcomes. The discovery source is recorded, and the table is also reported without these additions;
   - any independent source added under section 2.4.
2. **Inclusion.** A gold project enters if all of the following hold:
   - it has an economic study with an NPV and an IRR, on either a pre-tax or an after-tax basis;
   - the study is dated in the window, 1 January 2012 to 31 March 2022 (the end date of the stock-sample screen, so every source covers the whole window; every entry then has at least 48 months to the data cut-off);
   - the study is held by a company with no producing mine at the study date;
   - gold is at least 80% of the study's revenue.
3. **Exclusion.** A project is excluded if its construction was decided before its first study in the window. Projects held by producing companies are excluded; the table is labelled "projects held by companies with no producing mine at the study date". A project later acquired by a producer stays in, and is followed through the acquisition.
4. **Recall before counting.**
   - **ASX.** Recall is measured against the Australian Government's major-projects lists, as in Phase 4. Any study the lists hold and the frame misses is added if it meets section 2.2. Its discovery source is recorded, and the table is also reported without such additions.
   - **TSX and TSXV.** The full-text screen in section 2.1 measured the recall of the headline screen: the Phase 4 candidate list held about 90% of the companies the full-text screen flagged inside the Phase 4 company frame. For the Phase 4 panel, recall by outcome is computed from qualification decisions made without outcomes and reported with the Phase 4 results. Because the full-text screen's finds enter the frame, it cannot also audit the frame; measured against itself, the merged frame's recall would be 100% by construction. The write-up states that the frame is built from two screens by the same vendor, and that recall beyond both is unmeasured for TSX and TSXV.
   - **Earlier plan.** A property-level study database is not covered by the Capital IQ licence. SEDAR+ was tried as the TSX and TSXV list; its document-type and date filters could not be applied, so it gave no usable list.
   - **Revisit.** If a vendor-independent TSX and TSXV list of gold economic studies is found, recall is measured against it and reported by stage.
5. **Frame size.**
   - The frame count is recorded, after de-duplication, before any new label.
   - If it is below 120 projects, the frame is extended to studies dated 2008 to 2011 under the same rules. Those projects go into the estimate half.
   - If it is still below 120, the table is reported as descriptive, and no stability claim is made.

## 3. Stages

- **PEA:** scoping studies and preliminary economic assessments.
- **PFS:** pre-feasibility studies.
- **FS:** feasibility, definitive feasibility, bankable feasibility and FEED studies.
- An updated study keeps its stage. An optimisation or price re-run is not a new entry.

## 4. Entries

- **One entry per stage.** Each project opens at most one entry per stage, at its first study of that stage in the window. A project that moved from PEA to PFS to FS opens up to three entries.
- **Entry period.** An entry runs from its study date to the first construction decision, or to the end of follow-up. Moving to a later study does not end it, because projects normally reach construction through later studies.
- **Progression.** Movement to the next stage is reported as its own outcome.
- **Clustering.** Intervals come from a bootstrap over projects, so one project's entries are not treated as independent.
- **Check.** One entry per project, at its first study in the window.

## 5. Outcomes

- **Construction decision.** A decision by any owner, under the Phase 4 labelling rules (`docs/phase4/labelling.md`): a statement plus committed funding, dated at the later of the two.
- **Takeover.** A takeover of the owner is dated at the change of control. It does not end the entry; it gets its own cumulative-incidence curve.
- **Secondary competing-risks version.** The first event ends the entry. Fine and Gray, and cumulative incidence, are reported by stage.
- **Other events.** Abandonment is a non-event. A project sold to a new owner is followed.
- **Labelling.** New projects are labelled from company and public documents only.
- **Second coding.** A random 20% of rows, plus every row resting on press reports alone or marked low confidence, is coded a second time. The second coder has no access to the repository or to the first labels. How that was ensured is recorded.

## 6. Follow-up

- **Data cut-off:** 31 March 2026. Follow-up for each entry ends at the cut-off.
- **Censoring:** horizons not reached by the cut-off are censored, and rates use cumulative-incidence estimators.

## 7. Stability test

- **Split.** Entries with studies dated 2012 to 2016 form the estimate half. Entries dated 2017 to 2021 form the test half. Stock-sample entries dated 2022 belong to the test half. Entries added under section 2.5 (2008 to 2011) belong to the estimate half.
- **Results fixed in advance.** Three results are reported, each with the wording fixed here:
  - (a) **Stage adds information.** On the test half, compare the 36-month Brier score using the stage rates with the score using a single pooled rate. Report the difference with a bootstrap interval.
  - (b) **Order.** Whether, on the test half, the PEA rate is below the PFS rate, and the PFS rate below the FS rate.
  - (c) **Stability, per stage.** Take observed minus predicted 36-month incidence, with an interval that covers sampling noise in both halves. Report one of three readings:
    - "consistent": the interval includes zero and its half-width is 15 points or less;
    - "different": the interval excludes zero;
    - "too imprecise to judge": anything else.
- **Wording when rates differ.** If any stage is "different", the write-up says the rates moved between the two periods, and that the periods fall in different gold-price regimes.
- **Small cells.** A test-half stage cell with fewer than 5 construction decisions is reported as descriptive only.
- **No further strata.** Jurisdiction, size and exchange are reported descriptively only.

## 8. Comparison with practice (secondary)

- **Implied multiple.** Stage probabilities are converted into an implied NAV multiple through the engine, labelled as derived rather than observed.
- **Sell-side bands.** That multiple is compared with sell-side stage bands, once each band has been verified in its original source.
- **Two price measures.** Where prices exist, P/NAV and the price-to-built-value ratio are shown side by side.
