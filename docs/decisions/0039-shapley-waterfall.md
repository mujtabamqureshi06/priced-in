# 0039. Order-independent waterfall by Shapley value

- Status: accepted
- Date: 2026-11-16

## Context

The waterfall (WP 1.9) switches risks on one at a time. A risk's step therefore depends on the order. Stage failure, for example, scales every effect charged after it. WP 3.5 asks for an order-independent option.

## Decision

`report.shapley_waterfall` keeps the first two steps in sequence and gives each of the four risk steps its Shapley value (Shapley 1953):

- **Kept in sequence:** discounting at the valuation rate, and market gold prices. They set the valuation basis rather than measure a risk.
- **Shapley steps:** base timing, capital cost overrun, stage failure, and price uncertainty with the build decision.

A risk's Shapley value is its marginal effect averaged over all 24 orders. That needs 16 runs on common paths. Standard errors come from the same weighted combination applied path by path. Ramp-up stays a labelled zero (ADR 0029).

The sequential waterfall remains the default display. The Shapley version is reported beside it.

## Consequences

- Both versions sum exactly to the same total.
- A risk whose effect does not depend on the others gets the same step either way (tested).
- For Osino the two orderings agree on the ranking. The largest difference is the overrun step: -55.0 sequential against -51.9 Shapley.
