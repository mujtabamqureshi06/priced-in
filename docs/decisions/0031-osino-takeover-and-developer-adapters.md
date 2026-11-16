# 0031. Osino takeover and developer adapters

- Status: accepted
- Date: 2026-11-16

## Context

Three Osino prices exist: the developer's market value around the DFS (July 2023), Dundee Precious Metals' agreed offer of C$0.775 cash plus 0.0801 DPM shares per share (C$1.553, C$287 million fully diluted in the money; December 18, 2023), and Shanjin's (formerly Yintai) all-cash C$1.90 per share (about C$368 million; agreed February 25, 2024, after a superior proposal on February 19). The engine inverts equity-based prices as q(d) = price / V_pass(d) (`inversion.equity_frontier`).

## Decision

1. **From equity to project:** project price = equity value - net cash (latest Osino statements before each date) - other assets. Exploration ground is valued at zero and flagged: this overstates the project price and so the implied odds. For a developer's market value, also deduct the present value of corporate G&A burn (#69). If the equity value counts in-the-money options and warrants, add their exercise proceeds to net cash.
2. **Claim matching:** bids are compared with the project claim (the acquirer funds construction, so ADR 0030 dilution does not apply); undisturbed and developer market values are compared with the equity claim with dilution, under the ADR 0030 bound.
3. **Headline:** the undisturbed market value before the Dundee offer (close on December 15, 2023) is the headline; the bids are shown alongside, labelled "includes control premium and any synergies; overstates the odds on a standalone basis". Shanjin has no undisturbed price (Osino traded on the Dundee bid), so only the bid is shown.
4. **Timing:** the December 15 value uses Osino's own guidance then; DPM's plan (construction decision by Q3 2024, first production in H2 2026) applies only to its own offer; Shanjin's disclosure if any, otherwise Osino's latest guidance, flagged.
5. **Currency:** DPM's share consideration is valued at the C$1.553 disclosed at announcement; results are stated in C$ as disclosed, with dated conversions.

## Revisit if

An Osino disclosure values its exploration ground, or the circular itemises synergies.
