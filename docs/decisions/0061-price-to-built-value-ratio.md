# 0061. The headline number is the price-to-built-value ratio

- Status: accepted
- Date: 2026-11-19
- Amends: ADR 0055 rule 6, ADR 0056

## Context

The number the engine reads from a price is q = price / V_pass, where V_pass is the value of the claim on paths that pass every gate (built when the build rule allows). It is a probability only if paths that are not built are worth nothing, the price contains nothing but this project, and the required return is right. At a 0% spread none of these holds: V_pass is then close to the undiscounted after-tax cash flow at spot gold (methodology section 7), so q behaves like a P/NAV re-marked to spot gold at a near-zero rate. ADR 0055 rule 6 already said the level is never presented as odds; the website headline and example did present it that way.

The name is new. P/NAV is the established practitioner ratio. This ratio differs in its denominator: the value is computed at today's gold price, real rates and volatility under the market-consistent convention, after the capital overrun prior, the option not to build in bad price states, and financing dilution, rather than at an analyst's deck and a single risk-adjusted rate.

## Decision

1. The headline quantity is called the **price-to-built-value ratio**: the price as a share of what the project would be worth if built on schedule, at today's gold price, rates and volatility, after overrun, the option not to build and dilution.
2. "Implied odds" is used only as a conditional reading that names the required return, in the form "if a [x]% extra return were the only other thing separating price from value, this would be the implied odds of a build on schedule".
3. Public text that presented the ratio as a count of simulated outcomes ending in a built mine is reworded. The website headline becomes "How much of an unbuilt mine's value is in its price?"
4. Wherever the ratio is introduced to a reader who knows P/NAV, it is defined against P/NAV in one sentence.

## Consequences

- The website, README and app caption are reworded; the website test checks the new wording.
- Case notes and decision records keep "implied odds" where the reading names its required return or spread.

## Revisit if

A practitioner or academic source is found that names this quantity differently; adopt that name.
