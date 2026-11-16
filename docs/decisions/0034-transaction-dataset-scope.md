# 0034. Transaction dataset scope; White Dam is not a control

- Status: accepted
- Date: 2026-11-16
- Decided by: Mastermind (routine), applying the WP 2.7 rule that only deals with a public economic study are modelled

## Context

WP 2.7 builds `data/transactions.csv` from Vox's disclosed deals. WP 2.8 planned White Dam as a control: a producing royalty that should imply near-certain odds.

At the White Dam deal (agreement September 2, 2026; completed September 14, 2026; A$5.0M, which Vox records as US$3,590,400, for a 2.0% NSR), the operator was producing from the historical heap-leach pad. The pit restart still depended on an updated resource and a mining study that were under way. No public economic study covered the royalty ground on the deal date. The corrections register already marked White Dam as "not a clean control".

## Decision

1. Each row has one of four scopes: `modelled` (a case file exists), `planned` (a dated public study exists and the case is not yet built), `control` (a producing-royalty control under ADR 0026) or `listed` (kept for completeness, with the reason it is out of scope).
2. White Dam is `listed`, not a control. Building a schedule for it would need a mine plan the operator had not published, which is the Tier 2 test in ADR 0026 failing.
3. Kalman and Sylvania (one A$3.4M price for two royalties, with no split and no current study) and the February 2026 Australian portfolio (two royalties for one price, with part of the price contingent) are `listed`.
4. Wharf (Metalla, 2020) stays the producing control for WP 2.8. Sorby Hills is `planned` and needs silver and lead revenue (WP 2.6).

## Consequences

The back-test has one producing control, not two. The second-control search under ADR 0028 stays open. A study published for White Dam after September 14, 2026 cannot be used for this deal (ADR 0007, no look-ahead). Sellers are described by type only.
