# 0045. Reading a price at a third-party reference rate

- Status: accepted
- Date: 2026-11-16
- Supersedes in part: ADRs 0028 item 1, 0032 item 2, 0035 (the conversion of reference rates to spreads)

## Context

Several results read a price at a rate someone else published:
- Osisko's 2020 goodwill-test rate, 3.5% post-tax real;
- OR Royalties' 2025 rate, 5.1%;
- the Eight Capital fairness opinion, 10.5% to 13.5% real;
- each study's own rate (5%, 10%);
- the CIM survey's FS-stage rate, 8.9%;
- Lopatnikov and Rumyantsev's (2025) 16% real WACC for Twin Hills.

These were converted to spreads over the real risk-free rate as k - r and applied in market-consistent mode.

That conversion is wrong. Each source applied its rate to cash flows at a flat real price deck. In market-consistent mode, expected metal prices rise at the real rate r (zero convenience yield). For a revenue claim, (1 + r) / (1 + r + s) = 1 / (1 + k) gives s = k(1 + r), not k - r. For a project claim with fixed real costs, no single spread matches both sides. The error overstated spreads when r was negative (South Railroad, 2021) and understated them when r was positive (Sorby Hills, 2026; Osino, 2023).

## Decision

1. **Convention valuation.** A price is read at a third-party rate the way the source computed its own number:
   - metal prices are flat in real terms, at the source's own deck where it states one, otherwise at spot, labelled;
   - there is no volatility, and cash flows are discounted at the stated rate k;
   - our stage, delay and overrun risks apply on top.

   `Market.flat(price, k)` builds the market; for multi-metal royalties, `MetalsMarket` with a zero real rate and the rate entered as the spread.
2. **Decks used.** The decks are those stated in each source:
   - Osisko 2020: US$1,600 long-term gold (2020 statements, goodwill note, fair value less costs of disposal);
   - OR Royalties 2025: US$42 long-term silver (2025 statements, Note 12); lead at spot, since no lead price is stated;
   - Eight Capital: US$1,850;
   - Twin Hills DFS: US$1,750;
   - South Railroad FS 2022: US$1,650.

   Results at spot are shown as a sensitivity where the deck and spot differ.
3. **Double counting of stage risk.** It is avoided by what each rate was applied to:
   - Rates for unrisked or producing cash flows carry our risks on top. These are Osisko, OR Royalties, the studies' rates and Eight Capital.
   - Lopatnikov and Rumyantsev applied 16% to probability-weighted flows, so our risks on top match their method.
   - The CIM stage-based rate already includes development risk. It is shown as a value only, not converted to odds.
4. **The spread curve and the break-even spread stay in market-consistent mode.** The break-even spread is the headline measure and does not depend on any reference rate. On royalty charts a marker may be drawn at s = k(1 + r), labelled approximate where fixed payments such as advance royalties exist. No marker is drawn on project charts.
5. **Erratum.** The corrected values replace the old ones, and `CHANGELOG.md` states what was wrong with the old and new values.

## Consequences

- South Railroad at Osisko's rate and deck: odds 0.80 to 0.89, against 0.72 to 0.80 before; at spot, 0.66 to 0.74.
- Sorby Hills at OR Royalties' rate: the price is above the value of the plan built on time at both the source's deck and spot, so no odds solve. The break-even market-consistent spread, 2.3%, is unchanged.
- Osino prices at the fairness opinion's rates and deck: higher odds than before. These are reported in the case note and the back-test.
- `tests/test_engine.py` pins the equivalence. A royalty valued at k on a flat deck equals the market-consistent value at the spread k(1 + r); the old k - r gives a materially higher value.

## Revisit if

A source's method cannot be established. In that case the row is dropped, not guessed.
