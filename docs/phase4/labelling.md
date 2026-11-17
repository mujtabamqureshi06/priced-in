# Phase 4 labelling form and procedure

Applies protocol section 4 (ADR 0051). One row per project in `data/phase4/labels.csv`, using the columns of `data/phase4/labels_template.csv`. Every filled field cites a public document: title, date, URL and page. Labelling starts only after the inclusion list is frozen.

## Fields

| Column | Content |
|---|---|
| `project_id` | Panel identifier (lower case, underscores) |
| `project` | Project name as in the candidate source |
| `owner_at_entry` | Owner company at the first snapshot |
| `listing_at_entry` | Exchange and ticker at the first snapshot (for example `ASX:BGL`) |
| `entry_study` | First study in the window: `PEA`, `PFS` or `FS` |
| `entry_study_date` | Release date of that study |
| `entry_study_source` | Document, URL and page |
| `outcome` | `construction_decision`, `takeover`, `non_event` or `censored` (definitions below) |
| `outcome_date` | Date of the outcome; for `non_event`, the window end |
| `outcome_source` | Document, URL and page |
| `owner_changes` | Each sale or takeover of the project before the outcome, with date and source, separated by semicolons |
| `abandonment_note` | For `non_event`: impairment to nil, change of business, or none; with source |
| `search_log` | Where the outcome search looked (see the procedure below) |
| `second_coder` | `yes` if in the 20% blind recode sample |
| `second_outcome` | Recode result; disagreements are resolved by the rule below |

Financings (for the issue-discount prior, #94) go in `data/phase4/financings.csv`, one row per raise (columns in `data/phase4/financings_template.csv`):
- `project_id`, `announcement_date`;
- `issue_price` and the last close before announcement;
- `shares_issued`, plus `warrant_ratio`, `warrant_strike` and `warrant_expiry` for attached warrants;
- `source`.

## Outcome definitions

- **`construction_decision`:** the board announces a decision to proceed with construction, with funding committed or in place. A decision to "commence early works" without full funding does not count. The date is the announcement date.
- **`takeover`:** a takeover of the owner completes, or the project is sold, and the new owner does not announce a construction decision within the window. If it does, the outcome is `construction_decision`, dated from the new owner's announcement.
- **`non_event`:** no construction decision by the window end (36 months after the entry study), including abandonment.
- **`censored`:** only when the project cannot be traced after the full search procedure; the search log must show each step.

## Search procedure (each project, in order)

1. The owner's announcements (ASX platform or SEDAR+) from the entry study to the window end: search titles for "decision", "construction", "final investment", "FID", "funding", "takeover", "scheme", "sale", "impairment".
2. If the owner was acquired: the acquirer's announcements and annual reports for the window.
3. The government major-projects list for each later edition: stage changes, and removals with their stated reason.
4. News search on the project name and the window years.

Each step is recorded in `search_log`, including steps that found nothing.

## Second coding and disagreements

- **Sample:** 20% of projects, drawn at random with a recorded seed after the inclusion list is frozen. A second coder labels them blind to the first labels.
- **Disagreements:** go back to the primary document. If the document is ambiguous, the stricter reading applies: funding must be committed before an announcement counts as a construction decision. The resolution is noted in the row.
- **Construction-decision dates:** at least 20% of `construction_decision` dates are checked against the original announcement (ADR 0052), whether or not the project is in the recode sample.
