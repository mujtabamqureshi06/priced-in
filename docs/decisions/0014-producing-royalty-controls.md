# 0014. Producing-royalty controls for the buyer's required return (amends 0008)

- Status: accepted; clarified by ADR 0020 (price basis)
- Date: 2026-11-15
- Decided by: Independent Decision Maker (owner's proxy), decision record DR-002
- Amends: ADR 0008 (owner), by adding a fallback. The owner has been asked to review.

## Context

ADR 0008 calibrates the buyer's required return on royalty purchases over producing mines with published reserves and mine plans. White Dam does not qualify, and a first search found no clean single-asset gold example.

## Decision

Calibrate on deals (primary method), with an industry-convention cross-check and fallback.

1. **Definition.** The parameter is a constant real spread over the real risk-free rate at each deal date, applied to risk-neutral expected royalty cash flows in market-consistent mode. It is calibrated once and held fixed. It is never solved jointly with odds or timing.
2. **Control criteria.** (1) A disclosed cash price for a single royalty, or a disclosed allocation. (2) A producing mine at the deal date. (3) A public reserve-based life-of-mine plan dated before the deal. (4) A deal date of 2018 or later. (5) A simple NSR or GRR with no production thresholds. (6) Controls and target are valued on the same basis: the published life-of-mine plan only, so the spread absorbs any upside the buyer paid for; the method notes say so. (7) For a bundled deal, only an allocation the parties disclosed; never an estimated one.
3. **Fees.** The price is the buyer's total disclosed cost, for controls and target alike. South Railroad includes the US$99k finder's fee once confirmed.
4. **Non-gold controls.** A simple NSR on a fixed mine plan is linear in price, so its risk-neutral value needs only the futures curve at the deal date. Beyond the last liquid tenor, the last forward is held flat in real terms, flagged.
5. **Number.** At least two controls. The spread is held at the mean across controls. South Railroad's inversion is reported at the mean and at the lowest and highest control spreads, in addition to the sensitivity ADR 0008 requires.
6. **Search limits.** Search the disclosed acquisitions of listed royalty and streaming companies. If fewer than two qualify, relax only criterion (4), to 2015 or later. Never relax (2), (3), (5) or (7).
7. **Fallback and cross-check.** The convention rate (the real rate used for royalty NAVs) needs its own verified source. Cross-check: each control's implied single real discount rate in analyst mode, compared with the convention. Fallback, if fewer than two controls qualify: the convention rate less the real risk-free rate at the target's deal date, labelled in every output "industry convention, not a market calibration".
8. **Deals found so far.** Cozamin (Gold Royalty, US$7.5M for a 1.0% NSR on two concessions, 2023): eligible only if the published mine plan shows the production from the covered concessions. Nevada Gold Mines bundle: excluded (thresholds, paid in shares). Côté and Karlawinda: excluded (construction stage at the deal date).
9. **Framing.** Each control's spread is described neutrally as a calibration input. Never say a buyer's return was high, low or generous; never rank buyers or deals.

## Consequences

The South Railroad inversion cannot stall indefinitely. Revisit if South Railroad's implied cumulative odds at the lowest and highest control spreads differ by more than 20 percentage points (then decide whether to publish a range only), if a clean single-asset gold control appears, or if the cross-check and the controls differ widely for no deal-specific reason. The owner checks whether any chosen control's buyer is a company he is in talks with.
