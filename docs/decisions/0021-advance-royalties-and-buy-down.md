# 0021. Advance minimum royalties and buy-down for South Railroad

- Status: accepted
- Date: 2026-11-16
- Decided by: Independent Decision Maker (owner's proxy), decision record DR-008
- Condition under: ADR 0016

## Decision

1. **Buy-down:** none assumed. This overstates the royalty's value and pushes implied odds lower; every output says so.
2. **Crediting:** report frontiers for both cases. Headline: advance minimum royalties (AMRs) credited in full against the first royalty payments, because "advance" royalty normally means an advance against future royalties and Vox describes the payments that way. The credited case is labelled an interpretation of the term, not a disclosed term.
3. **When AMRs stop.** Paths that are eventually built: AMRs are paid every year from the deal date until production starts, including years of delay. Paths that fail a stage gate or reach the build-decision expiry (WP 1.6) without building: AMRs stop at that date, on the basis that the operator gives up the ground. Bias: if operators give up ground sooner or renegotiate, this overstates value and pushes implied odds lower.
4. **Amount.** C$120,000 a year, fixed in nominal Canadian dollars unless indexation is disclosed, converted to real US dollars with the inflation and FX in the as-of market snapshot. Public wording differs: Vox's release says "approximately" C$120,000, while some reports of it say "over" or "more than" C$120,000. The figure is therefore treated as a floor, which understates value and pushes implied odds higher; this is flagged.

## Consequences

The South Railroad inversion is not published without items 3 and 4 stated in `docs/cases/south_railroad.md`, and the frontier is shown under both crediting assumptions. Revisit if crediting, termination or indexation terms are disclosed, or if the two crediting frontiers differ by more than the spread between the lowest and highest control spreads (ADR 0014); crediting then becomes a headline range.
