# Methodology

Every equation the engine uses, with its source and the decision record that fixed it. The work package that built each part is named beside its heading.

## 1. Conventions

- Real terms in the valuation date's currency, with an as-of market snapshot and no look-ahead (ADR 0007).
- Market-consistent mode is the default; analyst mode exists for reconciliation (ADR 0012).
- Reproducible randomness (ADR 0011).

## 2. Commodity price models (WP 1.2)

Gold follows geometric Brownian motion, simulated with the exact solution in annual steps: S(t+1) = S(t) x exp((mu - sigma^2 / 2) + sigma x Z), with Z standard normal, so E[S(t)] = S(0) x exp(mu t). Gold is not modelled as mean-reverting because a one-factor mean-reverting model could not be fitted to gold (Schwartz 1997). In market-consistent mode mu = ln(1 + r) - y, with r the real risk-free rate and y the convenience yield (ADR 0024); in reconciliation the study's flat deck is used. Antithetic draws are available. Volatility is the trailing 10-year realised volatility of the daily gold series to the valuation date (ADR 0024).

## 3. Project cash flow (WP 1.3)

Schedule mode starts from the study's annual cash-flow table and changes only what depends on the gold price (`pricedin.project`):

- Gold revenue in period t: study gold revenue × P_t / P_deck. By-product revenue stays at the study deck in Phase 1.
- Revenue-linked costs (royalties, levies, selling costs named in the case) scale with total revenue in the same period.
- Tax: study tax + τ × Δ(pre-tax profit), where τ is the case's sourced marginal rate; a negative result pays zero and is carried forward as a credit (ADR 0018).
- Capital, operating costs and working capital follow the study.

With the study deck, the engine reproduces the study table exactly. At other prices it reproduces Osino's published after-tax NPV5 within 0.3% (US$1,500 to US$2,000/oz) and South Railroad's within -2.3% to +5.2% (US$1,200 to US$1,600/oz); South Railroad's pre-tax NPV5 is within 0.1%. The South Railroad after-tax gap comes from treating Nevada's net proceeds tax and federal tax as one rate.

## 4. Stage gates and delays (WP 1.4)

Time runs in whole years from the valuation date (ADR 0022). Each path draws once whether it passes the remaining stage gates, with the cumulative odds from `data/priors.yaml` (ADR 0013). A path that fails, fails at the build-ready year: the years to construction start plus any added delay. Added delay moves the whole study schedule later and is the timing dimension of the inversion.

## 5. Capital cost overrun and ramp-up (WP 1.5)

Each path draws one capital cost ratio, applied to initial capital (including contingency) and expansion capital, not to sustaining capital or closure (ADR 0015). The build decision does not see the draw: Bertisen and Davis (2008) measured overruns found after the construction decision, so the decision rule tests the project at the study's capital estimate and the overrun reaches cash flows only once construction starts. A rule that could see the draw would skip high-overrun paths and overstate value.

## 6. Build decision (WP 1.6; Longstaff-Schwartz in WP 3.2)

The fixed rule tests each year from the build-ready year until the window closes. It builds in the first year in which the project's after-tax NPV at that year's gold price, held flat, at the study's capital estimate and discount rate, reaches the hurdle. It never sees the overrun draw. A path the rule does not build before the window closes is not built. The extra capital from an overrun carries no tax shield, which slightly understates value on overrun paths.

## 7. Discounting (WP 1.7)

Cash flows fall at the end of each whole year after the valuation date. In market-consistent mode, simulated cash flows are expected under risk-neutral gold dynamics and discounted at the real risk-free rate, while project-specific risks (stage gates, overrun) are simulated at real-world probabilities without a further premium (Samis et al. 2006; ADR 0012). The engine therefore never reports a distribution of NPVs discounted at a risk-adjusted rate (Davis 1995). Analyst mode, a single risk-adjusted rate on expected cash flows at the study deck, exists only for reconciliation and for the analyst-mode cross-check of controls (ADR 0014). A royalty is discounted at the real risk-free rate plus the buyer's spread; under risk-neutral gold dynamics an ounce of royalty revenue t years out is then worth spot x e^(-yt) x ((1 + r)/(1 + r + s))^t, so the cost of delay to the royalty holder is about s + y and does not depend on r (ADR 0024; tested).

## 8. Claims: project, equity, royalty (WP 1.8)

The project claim is after-tax cash flow discounted at the valuation rate from the valuation date. A royalty pays rate x coverage x gold revenue on each path, discounted at the valuation rate plus the buyer's spread (ADR 0014). Advance minimum royalties are paid at the end of each year before the first production year, and stop at gate failure or when the build window closes; if credited, their total is recovered from the first royalty payments (ADR 0021). The equity claim (ADR 0030) is the operator's share of project value less the value transferred to new shareholders when the equity-funded part of initial capital is raised at a discount d to fair value: E x d / (1 - d), with E the actual initial capital (overrun included) less the debt share of the study estimate. Debt is raised at fair value and transfers no value. The headline assumes all-equity funding, the upper bound on dilution.

## 9. Waterfall decomposition (WP 1.9)

The waterfall switches risks on one at a time in a fixed order on the same random paths: the study NPV; discounting at the valuation rate with the study deck held flat; market gold prices (spot with its market-consistent drift); base timing; capital cost overrun; ramp-up (reported as not modelled until ADR 0019 is implemented); stage failure; and price uncertainty with the build decision. Each bar is the change in the mean value, with its Monte Carlo standard error. Step sizes depend on the order; an order-independent attribution is planned for Phase 3.

## 10. Inversion and the odds-timing frontier (WP 2.5)

One price cannot identify both the odds that a project is built and how late. For each added delay d (whole years on top of base timing, applied only to paths that pass their gates), the inversion finds the gate odds q(d) at which the royalty value equals the price. Because the gate draw is independent of price and overrun, value is linear in q:

value(q, d) = q × V_pass(d) + (1 - q) × V_fail, so q(d) = (price - V_fail) / (V_pass(d) - V_fail).

V_pass is the value on paths that pass (built when the rule allows; advances until production or until the window closes). V_fail is the advances paid until the base build-ready year on paths that fail (ADR 0025). All delays use the same price paths.

Two numbers summarise the frontier without a timing prior (ADR 0023): the zero-delay odds q(0), the lowest build odds consistent with the price if the project keeps to the schedule assumed at the valuation date; and the certain-build delay, where q reaches 1, interpolated between whole years. The frontier is tested for shape allowing for Monte Carlo noise; if it is not monotone its shape is reported instead. In market-consistent mode the cost of delay to a gold royalty holder is the buyer's spread plus the convenience yield (ADR 0024), so the slope of the frontier depends mostly on those two inputs. Neither summary number is "the market's odds".

## References

- Bertisen, J. and Davis, G. A. (2008). Bias and error in mine project capital cost estimation. The Engineering Economist 53(2): 118-139.
- Carpentier, C. and Suret, J.-M. (2009). Private placements by small public entities: Canadian experience. CIRANO 2009s-12.
- Council on Environmental Quality (2020). Environmental Impact Statement Timelines (2010-2018).
- Davis, G. A. (1995). (Mis)use of Monte Carlo simulations in NPV analysis. Mining Engineering 47(1): 75-79.
- Lopatnikov, A. and Rumyantsev, A. (2025). Mining Science and Technology 10(3) (reporting Sykes and Trench 2014 and Smith 2013).
- McNulty, T. (1998). Developing innovative technology. Mining Engineering 50(10): 50-55.
- Samis et al. (2006) and Schwartz (1997): cited as in the project's literature dossier; full references to be verified in the sources register.

Full bibliography with verification status: [sources.md](sources.md).
