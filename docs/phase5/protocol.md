# Phase 5 protocol: probability and timing of a construction decision by study stage

Status: fixed before the frame is counted and before any new outcome is labelled (ADR 0064; frame sources amended by ADR 0065 and coding rules added by ADR 0066, both before the frame was counted; labelling rules added by ADR 0067 after labelling and before any rate). Outcomes for the Phase 4 panel are already known. That is acceptable here because the table is a count by stage with no fitted parameters, and the rules below are fixed first.

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

6. **Coding rules (ADR 0066).** Fixed before the frame is counted, from the questions coders raised while checking studies blind to outcomes.
   - **Project identity.** Deposits studied separately become one project only when a later study by the same holder or its successor puts them explicitly in one mine plan. The combined project's entries start from the first study of any component. Components never combined stay separate projects. Intervals come from a bootstrap over linked groups. The table with components kept separate is reported beside the main table. Because linking uses later documents, the number of linked groups is reported by outcome.
   - **Evidence.** An entry opens only at a study that itself shows an NPV, an IRR and a stated discount rate in a primary document. Where no primary document survives, two independent press reports, each quoting the figures from its own reporting or from the release, may settle it; reprints of one wire story count once. Such entries are flagged low confidence and the table is also reported without them. A study withdrawn at the exchange's request opens no entry. A later study does not open an entry for an earlier stage.
   - **Holder and control.** The holder is the listed company that publishes the study as its own; listing (section 2.1) is judged on that company. A study is excluded if a producing company controls the project at the study date, directly or through a parent it controls: more than 50%, or exactly 50% when the producer is also the manager. A company whose stated business at the study date is royalties or streams is excluded; an operator developing its own mine that also holds royalties is not.
   - **Producing.** Test or bulk-sample mining counts only while under way at the study date. Processing-only trials and non-mining production do not. Producing status is taken from the holder's filings dated before each study.
   - **Construction before the first study.** Only a decision on, or start of, construction of the development the study describes counts. Exploration access, declines and early works do not, unless announced as the start of construction. A plant built by an earlier owner and closed, or never operated, makes the project a redevelopment, which is not excluded. The same holder's earlier construction of the development excludes it.
   - **Gold share.** Gold's share of revenue comes from the study's own revenue table, or else from payable metal at the study's prices, flagged. Every computed share between 77% and 83% is checked against the technical report's revenue table, and the computed share and its source are recorded either way.
   - **Study by study.** Producing status, control and listing are judged at each study's date. Entries open only at studies that meet them.
   - **Unresolved.** A second pass, also blind to outcomes, takes the rows that turn on a missing fact. The frame is reported with and without the rows that stay unresolved.
   - **Revisit.** If the control rule removes more than 15 projects, the frame is recounted against the 120-project floor before any label. If more than about a quarter of linked groups end in a construction decision while unlinked projects do so at a clearly lower rate, the table with components kept separate becomes the primary table.

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

### 5.1 Labelling rules (ADR 0067)

Fixed on 20 November 2026, after the outcomes were labelled and before any rate, table or comparison was computed. Labelling under the Phase 4 rules showed that about half the construction decisions found have no dated decision statement. The rules below are applied to every row mechanically. Where a rule departs from the Phase 4 rule, the table is also reported under that rule.

- **Decision without a dated statement.** The event is dated at the earliest document stating that construction of the development has started or has been approved, and that it is funded. A statement that the owner funds it from its own cash counts. Where no document ever states funding, the date construction of the development started is used, flagged low confidence. Early works are not construction. This departs from the Phase 4 rule, under which undisclosed funding did not count: a project being built has been decided, and leaving such projects out would understate how often projects are built from each stage. A robustness table codes these rows as no decision.
- **Committed funding.** A signed facility agreement, even with customary conditions precedent; closed equity; or the company stating that the project is fully funded. Not a term sheet, a commitment still subject to due diligence or credit approval, or a package that depends on money not yet raised.
- **Approval conditional on a permit.** Dated when the last permit the decision depends on arrives.
- **Construction before the debt is signed.** Where funding is documented, the event is dated when the full stated funding became binding. The number of events that fall inside or outside 36 months differently under construction-start dating is reported.
- **Development different from the study.** A construction decision is a funded decision to produce saleable product from the project's ore on a continuing basis, whatever the processing route. Trial mining and bulk sampling do not count. Developments smaller than the study's are flagged as partial, and a robustness table counts only developments at about the study's scale and route. The same definition is applied to the construction-before-study rule in section 2.2, and any change it makes to the frame is reported before rates.
- **Linked projects.** A decision to build any part of the combined mine plan counts. In the table with components kept separate, each component keeps its own outcome.
- **Takeover.** A change of control of the project's owner: another party gains more than 50% of the voting shares, or the owner's shareholders before the transaction end with less than 50% of the combined company. Exactly 50% is not a takeover, flagged. A reverse takeover that hands control to new holders counts. A merger in which the owner is the acquirer does not. Receivership and administration are not abandonment unless the project is written off or relinquished; a project sold out of receivership is followed under its new owner.
- **Second coding.** 35 projects drawn at random (seed 20261121, drawn after the frame was recorded), plus every row marked low confidence or resting on press reports alone, are coded again under these rules by a coder with no access to the repository or the first labels. The agreement rate is reported and every disagreement is resolved under the written rules.
- **Revisit.** If the no-statement fallback and partial developments together supply more than a quarter of all construction decisions, the table under the Phase 4 rule becomes the headline. If second coding changes more than three event labels, that is reported with the result.

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
