# 0053. Phase 4: pooled panel, entry rule and candidate checks

- Status: accepted
- Date: 2026-11-17
- Amends: ADRs 0051 and 0052

## Context

The licence does not include a usable mining property database, so ADR 0052's preferred route was replaced by a company screen in S&P Capital IQ Pro, run by hand by the licensed user. The screen covers 1,240 gold companies on the ASX, TSX and TSXV, including delisted, acquired and wound-up companies. News-headline flags and business descriptions narrowed it to 443 candidates for review.

ADR 0051 kept TSX and TSXV names out of the core test because company-website archives survive mainly for companies that survived. Canadian filings for inactive issuers remain public through SEDAR+ and its archive of legacy SEDAR filings, so that reason no longer holds for a complete company frame.

Checked against the government's major-projects lists, the screen catches about three in four ASX gold developers. Some missed companies built their projects and some did not.

The protocol's entry rule, "a first scoping study, PFS or FS between 2012 and 2021", can be read two ways when a project was studied before 2012: excluded, or entered at its first study inside the window.

## Decision

1. **Pooled panel.** ASX, TSX and TSXV projects form one panel for the primary test. ASX-only and TSX/TSXV-only results and an exchange indicator are specified now as checks.
2. **Entry rule.** A project enters at its owner's first study published inside the window that reports an after-tax NPV and IRR. Earlier studies do not exclude it; the number of earlier studies and the years since the first study are covariates. The strict reading, first study by any owner inside the window, is run as a check.
3. **Candidate sources.** The company screen is the frame. ASX developers in the government lists that the screen missed are added by name, and results are reported with and without them. One attempt is made to measure TSX and TSXV recall against an independent list, used for the audit only.
4. **Recall by outcome.** The screen's recall is reported separately for built and unbuilt projects. A gap above about 20 percentage points means results are adjusted for selection or presented as descriptive only.
5. **Inclusion checks.** Unresolved candidates are decided only from documents dated on or before the study. A random 10% of exclusions was re-checked by the same analyst and is reported as a self-check. Before the list is frozen, an independent reviewer given only the rules and public sources re-decides those exclusions and a random 10% of inclusions, and every disagreement is resolved under the written rules.
6. **Freeze.** The candidate list and protocol are frozen with a commit hash before any outcome is labelled. The repository holds company names, tickers, decisions and reasons, not vendor data fields.

## Consequences

- The provisional panel is well above the 30-project floor, so the predictive test, not only a case series, is feasible.
- Projects enter at different points in their life. The history covariates and the strict-rule check show whether long-history projects drive the result.
- Revisit if the independent check agrees on fewer than 90% of cases, if the after-tax rule removes more than a quarter of ASX entries at the PEA stage, or if the panel falls below 30 projects.
