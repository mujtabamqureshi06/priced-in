# ADR 0070: Phase 6 part 1, which royalty and stream deals are usable

- Status: accepted
- Date: 2026-11-25

## Context

ADR 0063 makes counting the first step of Phase 6. A deal must be usable before it is priced, "usable" must be defined before counting, and the count decides whether the phase is a test (25 or more deals), a case series (15 to 24) or merges into Phase 7 (below 15). The project has already priced or examined a few deals (ADR 0028, ADR 0034, ADR 0035), so the rules must not be shaped around them.

## Decision

1. Phase 6 part 1 follows `docs/phase6/protocol.md`, fixed before any deal is counted.
2. **Usable.** A disclosed price with at least 75% unconditional; no commercial production on the covered ground and gold at least 80% of study revenue; a public PEA, PFS or FS with after-tax NPV and IRR dated on or before the announcement and covering the ground; standard royalty or stream terms; one asset per price. Partial study coverage, past producers with a restart study, old studies, completion tests and related parties are flagged and reported with and without.
3. **Window.** Announcements from 2010 to October 2026, with the count from 2012 as a sensitivity.
4. **Search and coding.** A buyer list fixed before coding, with late additions logged; a second coder on a seeded 30% and every unclear deal; agreement reported for each rule.
5. **Deals already seen** are recoded neutrally, flagged, and reported with and without.
6. **Part 2** (spread range, width measure, scoring rule) is fixed after the count and before any pricing, by someone who has not first looked at the price amounts. `docs/phase6/count.md` holds counts only.

## Consequences

- The count can fall below 25, in which case the phase becomes a case series or merges into Phase 7, as ADR 0063 says.
- Private-fund purchases are found only where the other side disclosed them; the write-up states this recall limit.
