# Phase 5 frame, recorded before any new outcome label

Recorded 20 November 2026. Rules: `docs/phase5/protocol.md` (ADRs 0064 to 0066). No outcome of a project added in Phase 5 has been labelled at this commit. Outcomes of the Phase 4 panel projects were already known, as the protocol states.

## How the frame was built

1. **Sources.** The Phase 4 candidate list; the stock-sample screen; and a full-text screen of Capital IQ key developments whose description quotes NPV, IRR or after-tax figures (ADR 0065). Capital IQ was used only to find companies. No Capital IQ data is in this repository.
2. **Blind check.** About 265 companies were checked against the frame rules from documents dated at or before each study. The coders were not given outcomes or the reasons from earlier screens, and they recorded any later event they saw by accident without using it. Three further blind passes settled open questions, including ASX announcements read in a browser. A final pass checked 43 studies whose NPV, rate or IRR had not been confirmed.
3. **Coding rules.** Section 2.6 of the protocol: projects linked when a later study by the same holder or its successor puts the components in one mine plan; entries open only at studies whose own document shows an NPV, a stated discount rate and an IRR; studies excluded when a producing company controls the project, directly or through a parent; producing status, control and listing judged study by study.

## Counts

- **Projects: 171.** Three more could not be settled from the documents reached (Glenburgh, Mt Stirling, Dingman); results are reported with and without them.
- **Entries: 245**, one per project per stage, at the first qualifying study of that stage dated 1 January 2012 to 31 March 2022.

| Stage | 2012-2016 (estimate half) | 2017 to March 2022 (test half) | Total |
|---|---|---|---|
| PEA (including scoping) | 68 | 47 | 115 |
| PFS | 22 | 27 | 49 |
| FS (including DFS, BFS) | 40 | 41 | 81 |
| Total | 130 | 115 | 245 |

- **Unconfirmed studies.** Eight more entries would open if eight studies whose figures could not be confirmed from a document were counted. They are marked `in_lenient_only` in `data/phase5/frame_entries.csv` and are used only in a check.
- **Frame size.** The frame is above the 120-project floor (protocol section 2.5), so the 2008-2011 extension is not used.

## Files

- `data/phase5/frame_entries.csv`: one row per entry (project, stage, study date, holder at the study, tax basis of the figures, half, source documents).
- `data/phase5/linked_groups.csv`: the 13 projects whose components were studied separately before a later study combined them. Linking uses later documents, so these groups are reported by outcome after labelling (protocol section 2.6).

## Flags carried into the results

- Donlin Gold: a producing company held 50% without being sole manager; reported with and without.
- Mt. Hamilton: the holder described itself as an exploration and royalty company while operating the project; kept, flagged.
- Pine Grove: entry at a 2015 amended report whose economic inputs changed from the 2011 study.
- Studies resting on press reports or third-party copies are flagged and the table is also reported without them.
