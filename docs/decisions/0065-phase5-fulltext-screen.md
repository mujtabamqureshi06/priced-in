# ADR 0065: A full-text screen as a Phase 5 frame source, and what it can and cannot audit

- Status: accepted
- Date: 2026-11-20

## Context

The Phase 4 candidate list came from Capital IQ Key Development headlines that contain study words ("feasibility", "preliminary economic assessment", "scoping study", "study", "NPV", "reserve") for companies whose Primary Industry is Gold. The Phase 4 results state that TSX and TSXV recall was unmeasured, because no project-level independent list was found.

A second Capital IQ screen searches the description text of key developments, not only the headline, for NPV, IRR or after-tax figures, 2008 to 2022. It finds study releases whose headlines lack the study words, and companies that Capital IQ does not classify under Primary Industry = Gold. A first comparison at company level found about 90% of the companies it flagged inside the Phase 4 company frame already in the Phase 4 candidate list. The probable qualifying misses were judged after their outcomes had been seen, so that comparison cannot yet be used as evidence on selection by outcome.

## Decision

1. **Phase 4.** Each probable miss, and each borderline case, is confirmed by a coder who has the written rules and the primary documents and is not given outcomes. Recall by outcome is computed from those decisions, in both variants where a case is borderline, and judged against the 20-point trigger on the worse variant (protocol section 8). There is no rerun and no sensitivity run: the gap found so far is far below the trigger, and a run on entries chosen after outcomes were seen would add a weaker number. The addendum states that the figure depends on one vendor, is matched at company level, and cannot see releases that never quote an NPV or IRR.
2. **Phase 5 frame.** The full-text screen becomes a frame source (`docs/phase5/protocol.md` section 2.1). Every company it flags is checked, on the frame rules, blind to outcomes, including listed parents outside Primary Industry = Gold. The discovery source is recorded and the table is also reported without these additions. Studies dated 2022 enter only within the window the protocol already fixes; studies dated 2008 to 2011 enter only under the section 2.5 extension.
3. **Recall wording.** ASX keeps the government's major-projects lists as its independent audit. For TSX and TSXV, the write-up states that the frame comes from two screens by the same vendor and that recall beyond both is unmeasured.

## Consequences

- The Phase 5 frame grows by the qualifying projects the headline screen missed, and the counts are recorded before any new outcome is labelled.
- A screen used to build the frame is not presented as an audit of it.
- No Capital IQ data is committed; only derived counts are reported, credited to S&P Capital IQ.

## Revisit if

- The outcome-blind confirmation moves the recall gap by outcome above 10 points. The wording then names the direction of the gap.
- A vendor-independent list of TSX and TSXV gold economic studies is found.
