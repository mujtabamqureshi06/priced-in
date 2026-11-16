# 0041. Gold streams as strips of calls

- Status: accepted
- Date: 2026-11-16

## Context

Streams are the other main claim royalty companies buy (WP 3.6). In a standard stream, the holder pays an upfront deposit. It then receives a share of payable metal and pays, per ounce, the lesser of a fixed transfer price and spot.

## Decision

1. **Claim.** `engine.StreamClaim(share, transfer_price, transfer_escalation, spread)` values a gold stream on the same paths as every other claim.
   - Each delivered ounce is worth max(P - c, 0), so the stream is a strip of European calls on gold (Fuller 2023).
   - The transfer price is in real US$/oz at the valuation date and grows at a stated real rate. A price fixed in nominal terms has a negative real escalation.
   - The holder's spread is added to the valuation rate, as for royalties (ADR 0014).
2. **Not modelled.** The deposit is the price being read, so it is not a cash flow. Deposit reduction mechanics, delivery caps and step-downs are left out until a case needs them.
3. **Inversion.** A stream pays nothing on paths that fail a gate. Implied odds are therefore price / V_pass(d) for each delay (`inversion.stream_frontier`), as for equity (ADR 0031).
4. **Scope.** Gold only, on cases with a payable-ounce column and US$ money units. Silver streams wait for the multi-metal project engine (ADR 0036).

## Tests

- With deterministic timing and no gate risk, the simulated value matches the closed-form strip of Black-Scholes calls within Monte Carlo error.
- With a zero transfer price, the value equals the share of gold at market value.
- Synthetic recovery returns the known odds.
- Failing paths pay nothing.

## Consequences

A stream price can now be read the same way as a royalty price. No public stream deal has been modelled yet. A candidate needs a public gold stream with a dated study.
