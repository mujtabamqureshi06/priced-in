# ADR 0071: Phase 6 coding interpretations

- Status: accepted
- Date: 2026-11-25
- Amends: ADR 0070

## Context

First-pass coding under ADR 0070 found 429 deals on gold projects from 23 buyers. After a completion pass, 23 were usable and 20 unclear, against the threshold of 25 that separates a test from a case series (ADR 0063). The coders raised five points the written rules did not settle. They are decided here, after that count and before second coding, so the write-up discloses the timing and reports each point both ways.

## Decision

The five interpretations in `docs/phase6/protocol.md` section 7: unvalued warrants at notional value as an upper bound; buy-backs at fair market value standard and flagged; fixed-ounce deliveries not standard unless only a floor; a study counts from the first public date of its after-tax NPV and IRR; gold shares on head-grade or contained metal decide a deal only outside 70% to 90%. Deals still unclear after second coding are not usable.

## Consequences

- `docs/phase6/count.md` reports the usable count under each interpretation and its alternative.
- If the test or case-series outcome turns on one interpretation, the count says so.
