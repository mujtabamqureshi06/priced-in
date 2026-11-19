# Methodology

Every equation the engine uses, with its source and the decision record that fixed it. The issue that tracked each part is linked beside its heading.

## 1. Conventions

- Real terms in the valuation date's currency, with an as-of market snapshot and no look-ahead (ADR 0007).
- Market-consistent mode is the default; analyst mode exists for reconciliation (ADR 0012).
- Reproducible randomness (ADR 0011).

## 2. Commodity price models (#55)

Gold follows geometric Brownian motion, simulated with the exact solution in annual steps: S(t+1) = S(t) x exp((mu - sigma^2 / 2) + sigma x Z), with Z standard normal, so E[S(t)] = S(0) x exp(mu t). Gold is modelled as a random walk in the log price, as in Brennan and Schwartz (1985); mean-reverting and two-factor models are left to the copper work (ADR 0042). In market-consistent mode mu = ln(1 + r) - y, with r the real risk-free rate and y the convenience yield (ADR 0024); in reconciliation the study's flat deck is used. Antithetic draws are available. Volatility is the trailing 10-year realised volatility of the daily gold series to the valuation date (ADR 0024).

## 3. Project cash flow (#56)

Schedule mode starts from the study's annual cash-flow table and changes only what depends on the gold price (`pricedin.project`):

- Gold revenue in period t: study gold revenue × P_t / P_deck. By-product revenue stays at the study deck in Phase 1.
- Revenue-linked costs (royalties, levies, selling costs named in the case) scale with total revenue in the same period.
- Tax: study tax + τ × Δ(pre-tax profit), where τ is the case's sourced marginal rate; a negative result pays zero and is carried forward as a credit (ADR 0018).
- Capital, operating costs and working capital follow the study.

With the study deck, the engine reproduces the study table exactly. At other prices it reproduces Osino's published after-tax NPV5 within 0.3% (US$1,500 to US$2,000/oz) and South Railroad's within -2.3% to +5.2% (US$1,200 to US$1,600/oz); South Railroad's pre-tax NPV5 is within 0.1%. The South Railroad after-tax gap comes from treating Nevada's net proceeds tax and federal tax as one rate.

## 4. Stage gates and delays (#57)

Time runs in whole years from the valuation date (ADR 0022). Each path draws once whether it passes the remaining stage gates, with the cumulative odds from `data/priors.yaml` (ADR 0013). A path that fails, fails at the build-ready year: the years to construction start plus any added delay. Added delay moves the whole study schedule later and is the timing dimension of the inversion.

## 5. Capital cost overrun and ramp-up (#58)

Each path draws one capital cost ratio, applied to initial capital (including contingency) and expansion capital, not to sustaining capital or closure (ADR 0015). The build decision does not see the draw: Bertisen and Davis (2008) measured overruns found after the construction decision, so the decision rule tests the project at the study's capital estimate and the overrun reaches cash flows only once construction starts. A rule that could see the draw would skip high-overrun paths and overstate value.

## 6. Build decision (#59; Longstaff-Schwartz in #76)

The fixed rule tests each year from the build-ready year until the window closes. It builds in the first year in which the project's after-tax NPV at that year's gold price, held flat, at the study's capital estimate and discount rate, reaches the hurdle. It never sees the overrun draw. A path the rule does not build before the window closes is not built. The extra capital from an overrun carries no tax shield, which slightly understates value on overrun paths.

The optimal rule (ADR 0038) uses least-squares Monte Carlo (Longstaff and Schwartz 2001; ADR 0037).
- **Decision dates:** from the build-ready year to the end of the window.
- **Building now:** worth the market-consistent value of the project at that year, at study capital.
- **Waiting:** worth the regression estimate of continuing, fitted on independent paths with a cubic polynomial basis in the gold price.

The fixed rule remains the headline. At project-level spreads of 5% and above, the two rules agree for Osino within Monte Carlo error.

**Delay at zero convenience yield (ADR 0046).** In market-consistent mode with zero convenience yield and no spread, expected gold grows at the real rate while costs are fixed in real terms. Deferring construction then lowers the present value of costs but not of revenue, so project value rises with delay and the optimal rule waits to the end of its window. This follows from the zero-yield assumption (ADRs 0024, 0027), not from the projects. The Osino and South Railroad notes report the convenience yield, and separately the spread, at which one year of delay stops adding value; `tests/test_economic_sanity.py` asserts the behaviour. A holding cost per year of deferral (`Risks.holding_cost`, ADR 0049) can offset it. It is zero by default because no sourced figure exists, and the build decision does not include it.

The method is validated in two ways:
1. on the American put, against QuantLib finite differences (ADR 0037);
2. on the Brennan and Schwartz (1985) copper mine (ADR 0040). That mine has options to close, reopen and abandon, inventory as a discrete state, and a spline basis in the log price. All sixteen published values (eight prices, mine open and closed) are matched within one standard error.

## 7. Discounting (#60)

Cash flows fall at the end of each whole year after the valuation date, or half a year earlier when the study discounts on a mid-year convention (the study's t0 column stays at the valuation point; ADR 0043). Each case shows it reproduces its study NPV on the convention it uses. In market-consistent mode, simulated cash flows are expected under risk-neutral gold dynamics and discounted at the real risk-free rate, while project-specific risks (stage gates, overrun) are simulated at real-world probabilities without a further premium (ADR 0012). This follows the real-options practice of risk-adjusting the uncertain inputs and discounting the resulting cash flows with risk-free factors, so that cash flows claimed by different parties are each discounted for their own risk, rather than discounting net cash flow at one constant rate (Samis, Davis and Laughton 2007, pp. 128 to 129). The engine therefore never reports a distribution of NPVs discounted at a risk-adjusted rate (Davis 1995). Analyst mode, a single risk-adjusted rate on expected cash flows at the study deck, exists only for reconciliation and for the analyst-mode cross-check of controls (ADR 0014). **Third-party reference rates (ADR 0045).** A rate published by someone else (a royalty company's impairment-test rate, a fairness opinion, a study's own rate) is applied the way its source applied it: metal prices flat in real terms at the source's deck, or at spot where none is stated, no volatility, discounted at that rate (`Market.flat`), with this engine's stage, delay and overrun risks on top. It is not converted to a spread. For a pure revenue claim at zero convenience yield, a rate k on a flat deck equals a market-consistent spread of k(1 + r), not k - r; for a claim with fixed costs no single spread matches. The spread curve and the break-even spread stay in market-consistent mode. A royalty is discounted at the real risk-free rate plus the buyer's spread; under risk-neutral gold dynamics an ounce of royalty revenue t years out is then worth spot x e^(-yt) x ((1 + r)/(1 + r + s))^t, so the cost of delay to the royalty holder is about s + y and does not depend on r (ADR 0024; tested).

**The spread.** The spread is the buyer's real required return over the risk-free rate, on top of the risks the engine simulates (stage gates, overrun, gold price). It stands for what the model leaves out: a risk premium, illiquidity, and risks that are not modelled, such as permitting, jurisdiction and execution. One price cannot separate the spread from the build odds, because a higher spread and lower odds both lower the value. So every price is shown as a curve of odds against spread, with the break-even spread marked, or read at a spread taken from a qualifying producing-asset control (ADR 0014).

## 8. Claims: project, equity, royalty, stream (#61, #80)

The project claim is after-tax cash flow discounted at the valuation rate from the valuation date. A royalty pays rate x coverage x gold revenue on each path, discounted at the valuation rate plus the buyer's spread (ADR 0014). Advance minimum royalties are paid at the end of each year before the first production year, and stop at gate failure or when the build window closes; if credited, their total is recovered from the first royalty payments (ADR 0021). The equity claim (ADR 0030) is the operator's share of project value less the value transferred to new shareholders when the equity-funded part of initial capital is raised at a discount d to fair value: E x d / (1 - d), with E the actual initial capital (overrun included) less the debt share of the study estimate. Debt is raised at fair value and transfers no value. The headline assumes all-equity funding, the upper bound on dilution. Limited liability is applied at the build decision, not on each path (ADR 0059, superseding ADR 0047): with the build rule on, a path builds only if the value of building at that year's gold price, less the expected overrun and, for an equity run, the expected dilution, is not negative. After that, equity on a built path is not floored; a single path can be negative, and only expectations are reported. Takeover prices are read against the project claim, whose decision does not charge dilution.

Royalty terms not modelled: caps, production or value thresholds, step-downs, buy-backs and sliding scales. A royalty is a fixed rate on a fixed share of revenue, with optional advance minimum payments.

A gold stream (ADR 0041) delivers a share of payable gold to the holder against an ongoing payment equal to the lesser of a transfer price and spot. Each delivered ounce is therefore worth max(P - c, 0): the stream is a strip of call options on gold (Fuller 2023). It is discounted at the valuation rate plus the holder's spread. A stream pays nothing on failing paths, so its implied odds are price / V_pass(d), as for equity.

## 9. Waterfall decomposition (#62)

The waterfall switches risks on one at a time in a fixed order on the same random paths: the study NPV; discounting at the valuation rate with the study deck held flat; market gold prices (spot with its market-consistent drift); base timing; capital cost overrun; ramp-up (reported as not modelled until ADR 0019 is implemented); stage failure; and price uncertainty with the build decision. Each bar is the change in the mean value, with its Monte Carlo standard error. Step sizes depend on the order. The Shapley version (ADR 0039) keeps the first two steps in sequence and gives each of the four risk steps its average marginal effect over every order (Shapley 1953), from 16 runs on common paths.

## 10. Inversion and the odds-timing frontier (#71)

One price cannot identify both the odds that a project is built and how late. For each added delay d (whole years on top of base timing, applied only to paths that pass their gates), the inversion finds the gate odds q(d) at which the royalty value equals the price. Because the gate draw is independent of price and overrun, value is linear in q:

value(q, d) = q × V_pass(d) + (1 - q) × V_fail, so q(d) = (price - V_fail) / (V_pass(d) - V_fail).

V_pass is the value on paths that pass (built when the rule allows; advances until production or until the window closes). V_fail is the advances paid until the base build-ready year on paths that fail (ADR 0025). All delays use the same price paths.

Two numbers summarise the frontier without a timing prior (ADR 0023): the zero-delay odds q(0), the lowest build odds consistent with the price if the project keeps to the schedule assumed at the valuation date; and the certain-build delay, where q reaches 1, interpolated between whole years. The frontier is tested for shape allowing for Monte Carlo noise; if it is not monotone its shape is reported instead. In market-consistent mode the cost of delay to a gold royalty holder is the buyer's spread plus the convenience yield (ADR 0024), so the slope of the frontier depends mostly on those two inputs. Neither summary number is "the market's odds".

## References

- Brennan, M. J. and Schwartz, E. S. (1985). Evaluating natural resource investments. Journal of Business 58(2): 135-157.
- Bertisen, J. and Davis, G. A. (2008). Bias and error in mine project capital cost estimation. The Engineering Economist 53(2): 118-139.
- Carpentier, C. and Suret, J.-M. (2009). Private placements by small public entities: Canadian experience. CIRANO 2009s-12.
- Council on Environmental Quality (2020). Environmental Impact Statement Timelines (2010-2018).
- Davis, G. A. (1995). (Mis)use of Monte Carlo simulations in NPV analysis. Mining Engineering 47(1): 75-79.
- Fuller, E. W. (2023). An option-value framework for valuing mining streams. Resources Policy. doi:10.1016/j.resourpol.2023.103847.
- Longstaff, F. A. and Schwartz, E. S. (2001). Valuing American options by simulation: a simple least-squares approach. Review of Financial Studies 14(1): 113-147.
- Lopatnikov, A. and Rumyantsev, A. (2025). Mining Science and Technology 10(3) (reporting Sykes and Trench 2014 and Smith 2013).
- Maier, S. (2021). Re-evaluating natural resource investments under uncertainty: an alternative to limited traditional approaches. Annals of Operations Research 299(1): 907-937.
- McNulty, T. (1998). Developing innovative technology. Mining Engineering 50(10): 50-55.
- Shapley, L. S. (1953). A value for n-person games. In Contributions to the Theory of Games II, Annals of Mathematics Studies 28: 307-317.
- Samis, M. R., Davis, G. A. and Laughton, D. G. (2007). Using stochastic discounted cash flow and real option Monte Carlo simulation to analyse the impacts of contingent taxes on mining projects. Project Evaluation Conference, Melbourne, 19 to 20 June 2007, AusIMM, pp. 127 to 137. Read in full (open copy: https://inside.mines.edu/~gdavis/Papers/AusIMM.pdf).
- Further reading, not read in full and not relied on: Samis, M., Davis, G. A., Laughton, D. and Poulin, R. (2005). Valuing uncertain asset cash flows when there are no options: a real options approach. Resources Policy 30(4), 285 to 298.

Full bibliography with verification status: [sources.md](sources.md).

## Appendix: volatility from monthly average prices

The Phase 4 panel takes gold volatility from the World Bank's monthly series, which reports each month's average price (ADR 0057). Let the log price follow a random walk with variance σ² per month, observed at n equally spaced points a month, and let A_k be the average of month k. The change A_{k+1} − A_k is a weighted sum of the 2n − 1 increments between the first point of month k and the last point of month k+1, with weights rising from 1/n to 1 and falling back to 1/n. Summing the squared weights, each increment having variance σ²/n, gives

Var(A_{k+1} − A_k) = σ² (2n² + 1) / (3n²),

which tends to 2σ²/3 as n grows (Working 1960). Annualised volatility computed from monthly averages therefore understates σ by a factor close to √(2/3); `pricedin.volatility` divides the variance by 2/3. `tests/test_volatility.py` simulates a geometric Brownian motion with 21 trading days a month, averages it monthly, and checks that the variance ratio is 2/3 within 0.03 and that the corrected figure recovers the true volatility. On gold itself, monthly averages built from the daily series give 11.1% for 2012-2021 against 14.7% from daily returns; after the correction the World Bank series gives 13.5%.
