# Phase 5 results: how often does a gold study lead to a construction decision?

Status: complete. Rules are in `protocol.md`, `frame.md` and `labels.md`, and ADRs 0064 to 0069. Labels are in `data/phase5/labels.csv`; the table is computed by `scripts/phase5_stage_table.py`. Only derived results are shown here; vendor data are not redistributed.

## 1. Question and answer in one paragraph

A gold project held by a company with no producing mine has just published an economic study. How likely is a construction decision, by any owner, within 3 years? On 168 projects (170 once linked components are split) with studies dated 2012 to March 2022 and outcomes followed to 31 March 2026: about 8% after a PEA, 17% after a PFS and 47% after a feasibility study. Within 5 years: 17%, 30% and 59%. Within 3 years the owner is taken over in about 17% of PEA entries (twice the decision rate), 17% of PFS entries (the same as the decision rate) and 24% of FS entries (half the decision rate).

## 2. Primary table (linked components kept separate, ADR 0068)

Cumulative incidence of a construction decision by any owner, with 95% intervals from 2,000 bootstrap draws over projects (components of one linked group are drawn together).

| Stage | Entries | 12 months | 24 months | 36 months | 60 months |
|---|---|---|---|---|---|
| PEA | 113 | 1% (0 to 3) | 4% (1 to 9) | 8% (3 to 13) | 17% (10 to 24) |
| PFS | 47 | 0% (0 to 0) | 6% (0 to 14) | 17% (7 to 28) | 30% (18 to 44) |
| FS | 79 | 14% (7 to 22) | 28% (18 to 38) | 47% (36 to 58) | 59% (47 to 70) |
| All entries | 239 | 5% (3 to 8) | 13% (8 to 18) | 23% (17 to 29) | 33% (26 to 41) |

Every entry has at least 48 months of follow-up, so the 12, 24 and 36-month figures are plain proportions; only the 60-month column is censored (studies after March 2021).

**Linked table beside it** (groups as fixed with the frame): 9%, 19%, 48% at 36 months. With the one link that the blind re-check found only partly met (Gruyere-Yamarna) split: the same.

**One entry per project, at its first study:** PEA 7%, PFS 20%, FS 51% at 36 months (110, 25 and 35 projects).

## 3. Takeover of the owner (does not end the entry)

| Stage | 12 months | 24 months | 36 months | 60 months |
|---|---|---|---|---|
| PEA | 6% | 10% | 17% (10 to 24) | 28% |
| PFS | 0% | 11% | 17% (7 to 28) | 23% |
| FS | 10% | 16% | 24% (15 to 33) | 32% |

**Competing risks** (the first of decision or takeover ends the entry), 36 months: PEA 6% decision first and 16% takeover first; PFS 17% and 15%; FS 38% and 20%. Fine and Gray subdistribution hazard ratios against PEA: PFS 2.08 (1.29 to 3.41), FS 3.82 (2.73 to 6.14).

**Progression** (linked table, so that moves to combined studies count; observed only to 31 March 2022, the end of the study window): 32% of PEA entries reached a PFS or FS within 36 months; 44% of PFS entries reached an FS.

## 4. Stability test (wording fixed in protocol section 7)

- **(a) Stage adds information.** On the test half (studies 2017 to March 2022), the 36-month Brier score with pooled-rate forecasts minus the score with stage-rate forecasts is 0.010, 95% interval -0.029 to 0.042. The interval includes zero: on the test half, stage rates estimated from 2012-2016 did not forecast detectably better than one pooled rate.
- **(b) Order.** Test-half 36-month incidence: PEA 0%, PFS 28%, FS 41%. PEA below PFS below FS: yes.
- **(c) Stability, per stage** (test half minus estimate half, 36 months):
  - PEA: 13.4% then 0.0%; no decision within 36 months among 46 test-half PEA entries, so the cell is descriptive only.
  - PFS: 4.5% then 28.0%, difference +23.5 points (+5.4 to +43.5): **different**.
  - FS: 52.5% then 41.0%, difference -11.5 points (-32.9 to +11.1): **too imprecise to judge**.
- **Fixed wording that now applies.** Because PFS reads "different", the write-up says the rates moved between the two periods, and that the periods fall in different gold-price regimes. Figures for that sentence, checked 2026-11-25 against World Bank Pink Sheet originals (annual averages, gold, US$/troy oz): 1,670 in 2012 and 1,161 in 2015 (Pink Sheets of 6 January 2014 and 2 February 2017); 1,258 in 2017 (Pink Sheet of 3 April 2020) and 1,800 in 2021 (Pink Sheet of 4 December 2023). These match the secondary table used earlier (about 1,670, 1,160, 1,260 and 1,800). Estimate-half entries were followed mostly through falling or flat prices; test-half entries through rising prices.
- **Bootstrap.** Projects are drawn once, with their entries in both halves (18 projects have entries in both).

The linked table gives the same three readings.

## 5. Robustness (36-month incidence: PEA, PFS, FS)

| Reading | PEA | PFS | FS |
|---|---|---|---|
| Primary | 8.0% | 17.0% | 46.8% |
| Linked table, as fixed / with Gruyere-Yamarna split | 8.7% | 18.8% | 47.5% |
| Without Bardoc (primary / linked) | 8.0% / 8.8% | 17.0% / 18.8% | 46.8% / 47.5% |
| Witwatersrand Basin decided September 2025 (either table) | unchanged | unchanged | unchanged |
| Unconfirmed studies counted | 8.7% | 21.6% | 46.8% |
| With the 3 unresolved projects | 7.8% | 16.7% | 46.8% |
| Without studies resting on press or third-party copies | 7.5% | 18.2% | 46.6% |
| Without low-confidence labels | 7.1% | 15.0% | 45.2% |
| Without Donlin | 8.0% | 17.0% | 47.4% |
| Without full-text screen additions | 6.8% | 18.9% | 50.8% |
| Partial developments as no decision | 7.1% | 14.9% | 44.3% |
| Phase 4 rule (undisclosed funding is no decision) | 7.1% | 14.9% | 41.8% |
| Construction-start dating | 8.8% | 17.0% | 46.2% |

Construction-start dating changes the 36-month outcome of 1 entry and removes 1 entry whose construction started before its study. No ADR 0068 choice moves a 36-month stage rate by more than 2 points; the Witwatersrand alternative moves only the FS 60-month figure (Qala Shallows' FS is dated September 2021). The largest movements overall come from the Phase 4 funding rule (FS 5.0 points lower), counting unconfirmed studies (PFS 4.6 points higher) and dropping the full-text additions (FS 4.0 points higher).

Notes: the press flag is held per project, so a flagged project loses all its entries in that reading. Construction-start dates were not coded for linked components, so that reading applies to the other projects only.

## 6. Limits to keep in mind

1. The labelling rules (protocol section 5.1) were fixed after the outcomes were labelled and before any rate. The four calls in ADR 0068 were made after one run of the table; each is shown both ways above.
2. Second coding covered 101 of 174 projects; coders agreed on the event for 96 (`second_coded` and `second_coding_event_agree` in `labels.csv`). Six event labels changed against the first labels: five from rules fixed after the first labels and from the linked-projects rule, one (Mt Hamilton) from second coding tracing the project to the cut-off (list in `docs/phase5/labels.md`).
3. The frame comes from screens of one vendor's data (Capital IQ): the Phase 4 candidate list, the stock-sample screen and the full-text screen. Recall beyond them is unmeasured for TSX and TSXV; ASX recall was checked against the government's major-projects lists.
4. The fallback for decisions with no funding statement and partial developments supply 11 of 72 decisions (15%), below the quarter that would make the Phase 4 rule table the headline.
5. 25 labels are low confidence, 22 of them decisions (9 dated at construction start because funding was never stated, the rest for reasons recorded in each row). Removing them lowers the 36-month rates by 0.9 (PEA), 2.0 (PFS) and 1.6 (FS) points.

## 7. What it does not show

It does not say any project will or will not be built, and it is not a forecast for a named company. The rates describe projects of this kind in 2012 to 2022, under the gold prices of that time. The test half shows they moved between periods.

## 8. Comparison with practice (secondary)


**Implied NAV multiple (derived from build rates, not observed in prices).** The multiple of study NAV paid by a holder who values the project at its study NAV once construction is decided, and at nothing before: the expected discount factor to the decision within the horizon, primary table (`scripts/phase5_implied_multiple.py`, ADR 0069).

| Stage | 3 y, 5% | 5 y, 0% | 5 y, 5% | 5 y, 8% | 10 y, 5% |
|---|---|---|---|---|---|
| PEA | 0.07x | 0.17x | 0.15x | 0.13x | 0.25x |
| PFS | 0.15x | 0.30x | 0.26x | 0.24x | 0.36x |
| FS | 0.43x | 0.59x | 0.53x | 0.50x | 0.61x |

- Engine check: at the study's own deck, delaying construction by k years scales value by exactly (1 + r)^-k on all three gold cases (largest gap 3e-16), so the closed form is the engine's result.
- The 10-year column rests mostly on 2012-2016 studies, because later studies are censored.
- Left out: capital overrun, dilution, takeover premia, and value left in a project still unbuilt at the horizon. Each pushes a market multiple away from this one, in either direction.

**Sell-side stage multiples, read in the original.** Sprott Capital Partners, "Value in lackadaisical gold markets: adjusting to the new (old) multiples environment", 29 August 2022 (public PDF, https://sprott.com/media/5625/220826-pnav.pdf; page references checked against the PDF):
- Page 1, Table 1(A), "summary of P/NAV multiples applied": exploration 0.2-0.4x, PEA 0.2-0.5x, PFS/DFS 0.2-0.7x, construction 0.5-0.8x, production 0.6-1.5x.
- Page 2: target ranges of 0.5-0.7x NAV for gold developers with feasibility studies and 0.3-0.5x for explorers.

**Reading (orders of magnitude, not a test).** The derived FS multiple (0.53x at 5 years, 0.61x at 10 years, 5%) sits inside Sprott's feasibility band. The derived PEA and PFS multiples (0.15x and 0.26x at 5 years; 0.25x and 0.36x at 10 years) sit at or below the low end of Sprott's PEA and PFS/DFS bands. Sprott's multiples apply to the analyst's own NAV, on the analyst's price deck and development schedule, which often already pushes first production out; the derived multiple applies to the study NAV with construction at the decision date. So the comparison shows the two are of the same order, with build rates alone implying lower multiples at the earlier stages. It does not show that either is wrong.
