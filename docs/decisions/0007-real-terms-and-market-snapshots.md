# 0007. Real terms and as-of market snapshots

- Status: accepted
- Date: 2026-11-15

## Context

Technical studies mix conventions: most report constant (real) dollars at a flat price deck, some escalate costs, and observed prices (royalty deals, enterprise values, takeover offers) are set on a specific date in nominal currency. Mixing real cash flows with nominal discount rates, or valuing a 2021 deal with 2026 information, would produce numbers a reviewer could not defend.

## Options

1. Nominal terms throughout, with an inflation assumption.
2. Real terms throughout, with an as-of market snapshot per valuation.

## Decision

Option 2.

- All engine cash flows are in **real** terms of the valuation date's currency.
- Every valuation has an **as-of date** and a **market snapshot** taken at that date: commodity spot, a real risk-free curve and FX rates, each with a source.
- A study that escalates costs is converted to real terms, and the conversion is documented in the case file.
- **No look-ahead.** A case valued as of a date uses only information public on that date. Later events are used only for outcome tracking.

## Consequences

The snapshot becomes part of every case file. Each case write-up states the as-of date. For example, South Railroad is valued as of the Vox purchase (June 7, 2021) using only the March 2020 PFS; the 2022 and 2026 feasibility studies are outcome data.
