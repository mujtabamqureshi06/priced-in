# ADR 0067: Phase 5 labelling rules, fixed after labelling and before any rate

- Status: accepted
- Date: 2026-11-20

## Context

The Phase 5 outcomes were labelled under the Phase 4 rule: a construction decision is a statement plus committed funding, dated at the later of the two. About half the decisions found had no dated decision statement, and the labellers raised questions the rule does not answer: owners funding from cash, funding incomplete at the cut-off, approvals conditional on permits, construction before the debt is signed, developments that differ from the study, linked projects, and how to classify mergers.

## Decision

The rules in `docs/phase5/protocol.md` section 5.1 apply to every row. They were fixed after labelling and before any rate, table or comparison was computed, and the write-up says so. Where a rule is more generous than the Phase 4 rule (decisions with no funding statement, partial developments), the table is also reported under the stricter reading.

## Consequences

- The base rates count projects that were in fact built, including those built by owners who never published a dated decision.
- The stricter tables beside the main table show whether the choice of rule moves the rates.
- Second coding applies the final rules, and its agreement rate is reported.

## Revisit if

- The no-statement fallback and partial developments together supply more than a quarter of all construction decisions: the table under the Phase 4 rule becomes the headline.
- Second coding changes more than three event labels.
