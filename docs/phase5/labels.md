# Phase 5 outcome labels

Rules: `docs/phase5/protocol.md` section 5 and 5.1 (ADR 0067). Labels are in `data/phase5/labels.csv`, one row per project; `data/phase5/components.csv` holds the linked groups with components kept separate. Every label comes from company and public documents, cited in the `source` column. Follow-up ends on 31 March 2026.

## How the labels were made

1. **First labelling.** 174 projects (the 171 in the frame and the 3 unresolved ones) were labelled in seven batches. The coders had no access to the repository. Each row records the construction decision, takeovers, sales and abandonment, with a search log.
2. **Rules fixed.** The questions the coders raised were decided and written into section 5.1 before any rate was computed (ADR 0067).
3. **Second coding.** 101 projects were coded again under the final rules by coders with no access to the repository or the first labels: 35 drawn at random (seed 20261121, drawn after the frame was recorded), every first label marked low confidence or resting on press reports alone, and the rows named in the questions behind ADR 0067. Every project with a construction decision in the first labels was in the second-coded set.
4. **Resolution.** Each disagreement on the event, its date or the takeover list was settled by a separate coder who saw both codings and the written rules, checked the deciding documents, and recorded a reason. That covered 46 projects.
5. **Further checks.** The takeover test in section 5.1 was applied to the 32 first-coder-only rows that list a takeover. A component coding of the 13 linked groups gave each component its own entries and outcome. A construction-start date was found for every project with a decision, for the dating check in section 5.1.

## Agreement

- **Event.** The two codings agreed on whether a construction decision occurred by the cut-off for 96 of 101 projects (95%).
- **Date.** Where both had a decision (70 projects), the dates were identical for 34, within 90 days for 48, more than 90 days apart for 21, and more than a year apart for 4. Most large gaps came from when the full stated funding became binding.
- **Takeovers.** The takeover lists differed for 17 projects, mostly on whether a merger passed the more-than-50% test and on the date control passed.

## Label changes against the first labels

Six projects changed event label between the first labels and the final labels, more than the three that section 5.1 asks to be reported:

| Project | First label | Final label | Reason |
|---|---|---|---|
| South Railroad | decision | no decision | Approval conditional on permits; the last permit came after the cut-off |
| Kobada | decision | no decision | Funding package depended on money not yet committed at the cut-off |
| Witwatersrand Basin | decision | no decision | Senior debt still a credit-approved term sheet; committed funds below the stated requirement at the cut-off |
| Premier-Red Mountain | no decision | decision | Linked-projects rule: the Premier part of the combined plan was built |
| Bardoc | no decision | decision | Linked-projects rule: a funded 2015 start on Zoroastrian, a deposit in the combined plan; partial, low confidence |
| Mt Hamilton | untraceable | no decision | Second coding traced the project through later owners to March 2026; no decision found |

## Counts

- 72 projects with a construction decision by 31 March 2026, 102 without.
- Basis of the decision date: 57 statement and funding, 6 dated at the last permit, 9 construction start with funding never stated (low confidence).
- 6 decisions are partial developments, smaller than the study's or by a different route.
- The no-statement fallback and partial developments together supply 11 of the 72 decisions (15%), below the quarter at which section 5.1 makes the Phase 4 rule table the headline.

## Flags

- **Primary table.** The table with linked components kept separate is the primary table (ADR 0068). In it, a study that combines components belongs to no single component and opens no entry.
- **Link check.** A coder with no outcome information re-checked all 13 links against the written rule (`data/phase5/link_check.csv`): 11 pass, Gruyere-Yamarna is partial (Gruyere and Central Bore are in one plan; Attila South and Alaric, the open pits of the 2012 Yamarna study, are not), and Mallina is unclear because the deciding document could not be reached. The linked table is reported both as fixed with the frame and with Gruyere-Yamarna split.
- **Bardoc.** In the linked table the decision is dated before the group's 2020 PFS and 2021 FS, so those two entries open no follow-up. In the primary table the Kalgoorlie North component carries the 2015 decision and opens no entry of its own. Both tables are also reported without Bardoc.
- **Linked groups by outcome.** 8 of 13 linked groups ended in a decision, against 64 of 158 projects that were never linked.
- **Construction start.** `construction_start_date` is the earliest company or public document stating that construction of the development started; `construction_start_precision` says whether the day, the month (dated the 15th) or only the year (dated 1 July) is known. It is used only for the dating check in section 5.1.
