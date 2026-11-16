# 0036. Multi-metal royalties through a separate royalty-case module (WP 2.6)

- Status: accepted
- Date: 2026-11-16
- Decided by: Mastermind (routine engineering choice)

## Context

WP 2.6 asks for more than one metal: extra GBM price processes with a correlation input, revenue by metal, and a royalty on the metals the contract covers. Its test case, Sorby Hills, differs from the two Phase 1 cases in three ways:

1. it sells two priced metals and no gold;
2. its study is in A$;
3. it publishes pre-tax figures only.

The project-level template (`pricedin.inputs`) requires a gold revenue line, US$ money units and after-tax rows. The engine draws one gold price path.

## Options

1. **Generalise the template and the engine now.** This means metal-keyed prices everywhere, currency-aware money units, and an optional tax block. It touches the engine, waterfall, sensitivities, app and every script. It also stretches the ADR 0018 reconciliation test to a study with no after-tax figures.
2. **A separate royalty-case module** for royalties on projects whose construction decision is made. The value is then linear in each price, so it has a closed form under market-consistent dynamics. A correlated Monte Carlo is kept as a check.

## Decision

Option 2: `pricedin.royalty_cases`, with `price_models.CorrelatedGBM` for the correlated paths.

- **Money:** the study table is converted to US$ at the study's own deck exchange rate by period. Revenue is exactly payable metal times the US$ price, so the royalty needs no exchange-rate path.
- **Deductions:** treatment and refining charges are held at the study schedule.
- **Inversion:** implied odds of reaching production are price over value for each added delay, reusing `inversion.Frontier`.

Generalising the project engine to several metals moves to Phase 3, where copper, uranium and streams need it anyway.

## Consequences

- The Sorby Hills case reconciles to its FEED study on three checks:
  - payable silver and lead within 1% of the Table A11 totals;
  - NSR at the deck equal to the study rows;
  - pre-tax NPV within 1% under the mid-year convention, since the FEED's own convention is not stated.
- Volatility and correlation do not affect the royalty value. They matter once a build decision or a project claim is modelled.
- Fixed US$ deductions do not grow with prices. The value therefore depends weakly on the real rate even at a zero spread and zero convenience yield (tested).
