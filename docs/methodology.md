# Methodology

This document will hold every equation the engine uses, with its source. Sections are written in the work package named beside them. Conventions already fixed are stated now.

## 1. Conventions

- Real terms in the valuation date's currency, with an as-of market snapshot and no look-ahead (ADR 0007).
- Market-consistent mode is the default; analyst mode exists for reconciliation (ADR 0012).
- Reproducible randomness (ADR 0011).

## 2. Commodity price models (WP 1.2)

## 3. Project cash flow (WP 1.3)

Schedule mode starts from the study's annual cash-flow table and changes only what depends on the gold price (`pricedin.project`):

- Gold revenue in period t: study gold revenue × P_t / P_deck. By-product revenue stays at the study deck in Phase 1.
- Revenue-linked costs (royalties, levies, selling costs named in the case) scale with total revenue in the same period.
- Tax: study tax + τ × Δ(pre-tax profit), where τ is the case's sourced marginal rate; a negative result pays zero and is carried forward as a credit (ADR 0018).
- Capital, operating costs and working capital follow the study.

With the study deck, the engine reproduces the study table exactly. At other prices it reproduces Osino's published after-tax NPV5 within 0.3% (US$1,500 to US$2,000/oz) and South Railroad's within -2.3% to +5.2% (US$1,200 to US$1,600/oz); South Railroad's pre-tax NPV5 is within 0.1%. The South Railroad after-tax gap comes from treating Nevada's net proceeds tax and federal tax as one rate.

## 4. Stage gates and delays (WP 1.4)

## 5. Capital cost overrun and ramp-up (WP 1.5)

Each path draws one capital cost ratio, applied to initial capital (including contingency) and expansion capital, not to sustaining capital or closure (ADR 0015). The build decision does not see the draw: Bertisen and Davis (2008) measured overruns found after the construction decision, so the decision rule tests the project at the study's capital estimate and the overrun reaches cash flows only once construction starts. A rule that could see the draw would skip high-overrun paths and overstate value.

## 6. Build decision (WP 1.6; Longstaff-Schwartz in WP 3.2)

## 7. Discounting (WP 1.7)

## 8. Claims: project, equity, royalty (WP 1.8)

## 9. Waterfall decomposition (WP 1.9)

## 10. Inversion and the odds-timing frontier (WP 2.5)

## References

Full bibliography with verification status: [sources.md](sources.md).
