# ADR 0066: Phase 5 coding rules, fixed before the frame is counted

- Status: accepted
- Date: 2026-11-20

## Context

Coders checked about 265 companies against the Phase 5 frame rules, from documents dated at or before each study and without outcome information. They raised questions the protocol did not answer: how to treat deposits studied separately and later combined, what evidence opens an entry, who the holder is when a study is shared, when trial mining makes a holder a producer, what counts as construction before the first study, how to compute gold's share of revenue, and how listing changes between studies are handled.

## Decision

The answers are written into `docs/phase5/protocol.md` section 2.6 before any count:

1. **Linked projects.** One project when a later study by the same holder or its successor combines components in one mine plan; never-combined components stay separate. Bootstrap over linked groups. The table with components kept separate is reported beside. Linking uses later documents, so linked groups are reported by outcome.
2. **Evidence.** A primary document showing NPV, IRR and rate; two independent press reports may substitute, flagged, with the table also shown without them. Withdrawn studies open no entry.
3. **Control.** Producer control of the project at the study date, directly or through a controlled parent, excludes the study. The holder for listing is the listed publisher. Royalty and streaming companies are excluded; operators that also hold royalties are not.
4. **Producing, construction, gold share, listing.** Judged study by study from documents dated before each study, with the specific readings in section 2.6.

## Consequences

- Some projects held by listed developers drop out because a producer controlled them, including through a parent. If more than 15 drop out this way, the frame is recounted against the 120-project floor before any label.
- Linking deposits with knowledge of later studies could lengthen the follow-up of projects that were later built. The count of linked groups by outcome shows whether it does, and a stated trigger makes the unlinked table primary if it does.

## Revisit if

- The control rule removes more than 15 projects.
- More than about a quarter of linked groups end in a construction decision while unlinked projects do so at a clearly lower rate.
