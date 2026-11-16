# 0046. Delay raises project value at zero convenience yield

- Status: accepted
- Date: 2026-11-16

## Context

In market-consistent mode with zero convenience yield and no spread, expected gold grows at the real rate while costs are fixed in real terms. Deferring construction then lowers the present value of costs but not of revenue, so project value rises with delay. For Osino at the DFS date, with every gate passed, one year of delay adds US$23.6 million, and at zero spread the optimal build rule waits to the end of its window (mean build year 6.0 against 1.0 for the fixed rule). The case note said so; the methodology and README did not, and no test covered the published mode.

## Decision

1. The behaviour is stated in `docs/methodology.md` (section 6) and the README, as a consequence of the zero-convenience-yield assumption already flagged in ADRs 0024 and 0027.
2. `tests/test_economic_sanity.py` asserts it: in market-consistent mode at zero convenience yield, value rises with delay; at a 5% convenience yield, it falls.
3. The Osino and South Railroad notes report a diagnostic (`pricedin.sensitivity.delay_threshold`): the convenience yield, and separately the spread, at which one year of delay stops adding value. Both come out of the model, so no unsourced number is added. For Osino they are 1.07% and 2.54%. At South Railroad in June 2021 the real rate was negative, so delay already lowers value.
4. Sourced holding costs already accrue during delay:
   - Advance royalties at South Railroad are paid until production starts, so a delay adds payments. This applies to the royalty claim.
   - Corporate G&A in the market-value adapters is deducted over the years to start. Every published market-value reading is at zero added delay.
5. A generic holding cost (care and maintenance, land and permit costs) is not added now. It would need a new prior with no source.

## Revisit if

A source for holding costs on development projects is found.
