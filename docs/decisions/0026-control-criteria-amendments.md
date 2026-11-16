# 0026. Producing-royalty controls: share consideration, mine-plan tiers, one-control rule (amends 0014)

- Status: accepted
- Date: 2026-11-16
- Amends: ADR 0014, criteria 1 and 3, and the fallback in item 7

## Context

A first screen of disclosed acquisitions by Gold Royalty, Metalla, Elemental and Vox found two possible controls. Cozamin (Gold Royalty, 1.0% NSR on portions of Capstone's producing copper-silver mine, US$7.5M cash, announced 2023-07-31, closed 2023-08-30) needs the covered concessions mapped to the mine plan. Wharf (Metalla, 1.0% gross value royalty on Coeur's producing heap-leach gold mine, US$5.77M of which US$1.0M cash and 899,201 shares, closed 2020-06-30) is paid mostly in shares and has no recent technical report before the deal. Excluded on the criteria: Côté (construction), the Nevada Gold Mines bundle (thresholds, shares), the Monarch package (bundle, per-tonne), Higginsville (capped derivative), La Encantada (capped, in a bundle).

## Decision

1. **Criterion 1 now reads:** "disclosed consideration, cash or shares valued at closing-date fair value, for a single royalty." Shares are valued as recorded in the buyer's audited statements; the release value is used only if the statements do not itemise the acquisition, labelled "release value". Each control is labelled with the share of its price paid in shares. Cash controls are preferred when both kinds qualify.
2. **Criterion 3, two tiers.** Tier 1: a reserve-based annual schedule published before the deal and covering the deal date onward. Tier 2: for a mine with at least three years of steady production before the deal, a schedule built only from disclosed figures (latest reserve statement before the deal, run at the operator's latest guidance before the deal or the latest actual annual production, at reported recovery and payability, until reserves are exhausted), labelled "constructed from disclosed reserves and rate", with the guidance range as its sensitivity. A schedule from a technical report out of date at the deal date is not acceptable.
3. **Cozamin:** the covered concessions are mapped to production only from Capstone's named concessions (land tenure and production by zone), never inferred. The option on five further concessions is excluded from value while the full price is kept; this slightly overstates the price of the core royalty and lowers the implied spread, and is stated.
4. **If only one control qualifies:** one more search pass (Sandstorm, Triple Flag, Osisko, Maverix, EMX, Nomad, Franco-Nevada, Royal Gold; royalties only), with the deal date relaxed to 2015 or later as ADR 0014 allows. If still one: do not average; find a verified source for the industry convention rate and report the South Railroad frontier at both the control's spread and the convention converted to a spread, as a range labelled "one market control and one industry convention", with no single calibrated point. If there is no verified convention source or no control: report the frontier on a published grid of spreads, marked illustrative, with no headline point.

## Conditions

- Wharf's reserves have been replaced year after year; under criterion 6 its spread absorbs expected life extension and is pushed down. Each control's spread is shown separately with a one-line note on plausible upside beyond reserves, not quantified.
- Each control's buyer and seller are checked for conflicts of interest (ADR 0014).
- No spread is fixed until the candidates have been compared side by side, with each control's analyst-mode implied rate next to the convention cross-check.

## Revisit if

- Two or more cash controls qualify: Tier 2 and share-paid controls then become sensitivities.
- The two anchors in item 4 move South Railroad's zero-delay implied odds by more than 25 percentage points.

Confidence: high on items 1 and 2; medium on item 4.
