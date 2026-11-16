# 0048. Osino market value at the DFS, and dilution by series

- Status: accepted
- Date: 2026-11-16
- Amends: ADRs 0031 and 0033

## Context

ADR 0031 lists three Osino prices. The first, the developer's market value around the DFS (filed July 13, 2023), was not read because the last balance sheet published before that date had not been retrieved (#90). Osino's interim statements at March 31, 2023, and the MD&A for that quarter, are now in hand from the company's archived website.

The circular gives Osino's July 2023 trading range, C$1.07 to C$1.20 (p. 109), not a closing price on July 13. The only vendor series reachable for that date is the thin US over-the-counter listing.

Reading the September 30, 2023 statements again for this work showed two simplifications in the December 15, 2023 reading:
- restricted and deferred share units (2.91 million and 0.11 million) were left out;
- warrants were counted as one block at their C$1.28 weighted average, although one series (2.06 million at C$0.88) was in the money at C$1.13.

## Decision

1. **Price.** The July 2023 market value is read at both ends of the trading range, C$1.07 and C$1.20, as a band. No single-day close is used.
2. **Balance sheet.** March 31, 2023 statements, with the subsequent events they disclose:
   - broker warrants exercised in April 2023;
   - the Nebari second tranche drawn in May 2023, which leaves net debt unchanged apart from the US$50,000 fee, and whose warrants are out of the money in the range.
3. **Cash spent after March 31.** The Q1 MD&A implies about C$4.6 million spent between March 31 and May 29, 2023. This is shown as a sensitivity, not the headline, because it is approximate.
4. **G&A.** Corporate G&A of C$1.725 million for the quarter (Q1 2023 MD&A), annualised to C$6.9 million, is deducted as in ADR 0033.
5. **Dilution by series (all market-value readings).**
   - Each option and warrant series counts when the share price is above its strike, and its exercise proceeds then reduce net debt.
   - Share units always count and bring no proceeds.
   - Options stay at their weighted average, because the statements give no breakdown by strike.
   - Warrant strikes are in C$. The statements label the first Nebari series "US$0.88", but Note 12 gives its strike as US$0.65, and the September 2023 weighted average of C$1.28 only reconciles with C$0.88.
   - Offer prices are unchanged, because every series is in the money at both offers.
6. **Fairness opinion.** The Eight Capital opinion is dated December 17, 2023, after this price, and is labelled so (ADR 0033).

## Consequences

- `scripts/osino_prices.py` reads the July range, the December undisturbed value and both offers, each on its own balance sheet.
- The December 15 undisturbed price rises from C$195.7 million to C$199.6 million. Its break-even spread moves from 18.2% to 18.1%. The CHANGELOG records the change.
- The July 2023 reading uses the circular's trading range. The range was recorded in an earlier reading without a note of which copy was read, so its status is S until it is re-checked against the filed circular on SEDAR+.
