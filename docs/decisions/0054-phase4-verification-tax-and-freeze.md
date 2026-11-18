# 0054. Phase 4: verification, rule interpretations, tax method and freeze

- Status: accepted
- Date: 2026-11-17
- Amends: ADRs 0051 and 0053

## Context

ADR 0053 required an independent blind check before the candidate list was frozen. The first blind check agreed with the working list on 83% of sampled cases, below the 90% bar. Every inclusion was then verified from the study documents against the written rules, and the rules were extended where cases showed them to be ambiguous.

Reading the study documents showed that many Australian studies report pre-tax figures only, by local convention. Under ADR 0053's entry rule, which required an after-tax NPV and IRR, those projects could not enter at their first study. The trigger set for this case in ADR 0053 fired.

Some ASX companies have since delisted, and their announcements are no longer on the ASX site. After one final search of archives, company and acquirer sites, the announcements that could not be found were treated as unavailable.

## Decision

1. **Verification.** Every inclusion was verified against all rules from documents dated on or before its study, and the builder's inputs were recorded from the same documents. A second blind check (20 inclusions and 10 exclusions, seed 20261118, rules given verbatim, reviewer without access to the working files) set the bar for freezing at 90%. It agreed on 27 of 30 decisions and on the entry study for 13 of the 17 projects both sides included. Resolving every disagreement under the written rules showed the working list wrong on 4 of 30 cases when entry studies are counted. The error class found, an entry that skipped an earlier in-window study reporting pre-tax figures only, was then checked across every inclusion; no further entry moved.
2. **Written interpretations.** Fifteen interpretations of the rules are fixed in the protocol (section 2), including: documents within 45 days of a study count and are dated when the figures became public; the owner must be listed at the study date; a change of name is the same owner; only an earlier owner's entry-opening study blocks a later owner; a construction decision or start before the study excludes the project, but a mine built and closed by an earlier owner that needs a new restart decision is a redevelopment and qualifies; ownership comes from a document dated before entry, never from inference; press reports never decide.
3. **Study qualification.** An NPV at 0% counts. A study with no stated discount rate does not qualify. A study whose gold price is neither stated nor derivable from its own figures does not qualify. Where a release presents several cases, the case it labels as base is used; if none is labelled, the case the release headlines, else the middle case, flagged as judgment.
4. **Entry rule: two panels.** The primary panel uses ADR 0053's rule: a project enters at its first in-window study that reports an after-tax NPV and IRR, and leaves the primary panel only if no such study exists. The check panel lets a study reporting pre-tax figures only open an entry, with after-tax values modelled by the method in `docs/phase4/tax_method.md`, which was committed before its validation was run. The roles were set by item 5.
5. **Tax validation.** On the 51 panel studies that report both bases, the builder calibrated to pre-tax figures and taxed at the jurisdiction's statutory combined marginal rate gave after-tax NPVs with a median absolute error of 10.6% and a median signed error of -10.5%: statutory marginal rates without accelerated depreciation, depletion or loss carry-forwards tax more than the studies do. The threshold set in advance was 10%, so tax-modelled entries are kept out of the primary test. A defect found after the run (mixed US$ and C$ inputs in 12 Canadian releases) is fixed, and both runs are reported; no correction factor is fitted.
6. **Unavailable documents.** Candidates whose deciding document could not be read after the final search are dropped, with the reason recorded. Most are ASX companies that have since delisted, a group weighted toward companies later taken over or built. Drop counts are reported by exchange and, once outcomes are labelled, by outcome, and the TSX and TSXV-only result is reported beside the pooled result so the effect of the drops is visible.
7. **Construction period.** Where a study does not state one, the default comes from the panel's own studies that do: 1 year at or below the median initial capital, 2 years above it. The other value is run as a check.
8. **Freeze.** The list is frozen after the blind check's disagreements were resolved and the error class it found (entries that skipped an earlier study reporting pre-tax figures only) was re-checked across every inclusion. The commit that freezes the list also designates the primary panel and the check panel. No outcome had been labelled at that point.

## Consequences

- The primary panel loses projects whose only in-window studies report pre-tax figures, most of them in Western Australia. The ASX share of the primary panel falls, and the TSX and TSXV-only check keeps its role.
- The tax-modelled check panel shows whether including those projects changes the result.
- Revisit if the primary panel falls below 60 projects (power is then recomputed), or if the construction default differs from a size rule at US$200 million for more than a third of the projects that need it.
