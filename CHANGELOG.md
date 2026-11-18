# Changelog

All notable changes are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Phase 4 candidate list frozen (ADR 0054, `data/phase4/candidates.csv`): 447 candidates, 142 verified from study documents, 85 projects in the primary panel and 90 in the check panel, before any outcome was labelled. Two blind checks, sixteen written rule interpretations, and a re-check of every entry for the error class the second check found. Candidates whose deciding document could not be read are dropped and counted by exchange.
- Pre-tax calibration in `pricedin.parametric`: a study reporting pre-tax NPV and IRR only is calibrated to them, with tax modelled from a regime written down in advance (`docs/phase4/tax_method.md`, `data/phase4/tax_regimes.csv`, 40 jurisdictions with sources). Validated on 51 studies reporting both bases: median absolute error 10.6%, above the 10% threshold, so tax-modelled entries form a check panel and the primary panel keeps the after-tax entry rule.
- Phase 4 panel and entry rule (ADR 0053): ASX, TSX and TSXV projects pooled, with exchange-only checks; a project enters at its first study in 2012 to 2021 that reports after-tax NPV and IRR, with study history as covariates and the strict first-study rule as a check; candidates from a Capital IQ Pro company screen (1,240 gold companies, delisted included) plus government-listed ASX developers the screen missed; recall audited by outcome; independent check of a sample of decisions before the list is frozen.
- Phase 4 sources (ADR 0052): Capital IQ for prices and share counts, exported by the licensed user, with only derived results published; a mining property screen as the preferred candidate frame, with the government list as a pilot fallback. Candidate list extended to the 2017 to 2019 editions.
- Parametric study builder (`pricedin.parametric`, ADR 0051): an annual schedule from a study's headline figures, calibrated to its after-tax NPV and IRR. On Osino's DFS headline it tracks the transcribed case within 0.6% at market prices (informative; the Phase 4 validation uses a random ASX subsample).
- Phase 4 panel protocol, draft (`docs/phase4/protocol.md`, ADR 0051): ASX core panel, outcome coding, parametric mine plans with a hand-transcribed validation subsample, power table. Frozen before any outcome data is collected.

## [1.0.0] - 2026-11-16

### Fixed (erratum)
- **Reference rates were converted to spreads incorrectly** (ADR 0045). Third-party rates (Osisko's and OR Royalties' impairment-test rates, the Eight Capital fairness opinion, the studies' own rates, the CIM survey, Lopatnikov and Rumyantsev) were applied as a spread of k less the real risk-free rate. Those rates were set against flat real price decks, while the engine's metal prices rise at the real rate. For a revenue claim the equivalent spread is k(1 + r), not k - r, so the old readings overstated spreads when the real rate was negative and understated them when it was positive. Reference rates are now applied the way their sources applied them: prices flat in real terms at the source's own deck (or at spot where none is stated), discounted at the stated rate. Corrected values:

  | Result | Published in v0.2.0 and later | Corrected |
  |---|---|---|
  | South Railroad, Osisko 3.5% to 4.76% | odds 0.72 to 0.80 | 0.80 to 0.89 at Osisko's US$1,600 deck; 0.66 to 0.74 at spot |
  | Osino undisturbed value, Eight Capital 10.5% to 13.5% | 0.38 to 0.53 | 0.71 to about 1 at its US$1,850 deck; 0.49 to 0.65 at spot (includes the dilution correction below) |
  | Osino, Dundee offer | 0.40 to 0.51 | 0.72 to 0.98; 0.53 to 0.69 at spot |
  | Osino, Shanjin offer | 0.48 to 0.62 | 0.92 to no solution; 0.67 to 0.86 at spot |
  | Sorby Hills, OR Royalties 5.1% | 0.99 | no solution: the price is above the value of the plan built on time, at OR's deck and at spot |
  | Gold Standard offer, FS 5% and 10% (in #97, unreleased) | 0.39 to 0.66 | 0.64 to 0.74 at 5%; no solution or 0.87 at 10%, depending on timing |

  The break-even spreads, which use no reference rate, are unchanged apart from Monte Carlo noise. The back-test's statement that implied odds rise with stage was removed: the rows use different claims and rates and cannot be ranked.
- Published tables now use 200,000 paths, and the standard errors are shown. At 20,000 paths, Osino's headline value (US$899M) was one draw with a standard error of 5.8; it is now US$908M (standard error 1.8). Published break-even spreads moved by up to 0.2 points from the path count.
- The equity claim is floored at zero on each path (limited liability, ADR 0047). Takeover prices are read against the unfloored project claim (`inversion.project_frontier`). The floor raised the break-even spreads of the equity readings: Osino undisturbed from 16.9% to 18.2%, Gold Standard undisturbed from 10.0% to 10.8% (4-year timing) and from 15.5% to 16.8% (1-year).
- Osisko's and OR Royalties' rates are labelled as goodwill-test rates on fair value less costs of disposal, not value in use. Other corrections:
  - average real overrun 15.2%, not "about 14%";
  - Brennan and Schwartz: sixteen published values, not eight;
  - the in-sample bias of the replication is not one-sided.
- Osino's December 15, 2023 undisturbed value now counts dilutive securities series by series, and includes restricted and deferred share units (ADR 0048). Before, warrants were treated as one block at their weighted-average strike, and share units were left out. The price rises from C$195.7 million to C$199.6 million, and the break-even spread moves from 18.2% to 18.1%. The two offers are unchanged.
- Samis et al. (2006) and Schwartz (1997) were cited from secondary sources. The discounting rule now cites Samis, Davis and Laughton (2007), read in full. The gold-model rationale cites Brennan and Schwartz (1985).

### Changed
- Methodology section 7 defines the spread and says why one price cannot separate it from the odds. The Osino note sets the fairness opinion's P/NAV ranges beside the prices (0.27x to 0.56x of the DFS NPV) and explains why a multiple is not a probability.
- Osino's July 2023 trading range (C$1.07 to C$1.20) is now verified against Osino's own copy of its March 25, 2024 circular, p. 97 (status V); the earlier "p. 109" reference is corrected.
- Work items are now GitHub issues (#48 to #94); documents, decision records and code refer to issue numbers. The Brennan and Schwartz (1985) benchmark values were checked against the original article (status V).
- Editorial pass on the documentation for public release: internal process notes removed from the decision records and changelog; no decision changed (ADR 0001). ADR 0009 renamed `0009-thin-slice-sequencing.md`.

### Added
- LBMA PM cross-check of every gold snapshot (#93, ADR 0050). The vendor closing price stays the gold spot: on the four dates where the two differ by more than 0.5%, it is within 0.24% of a 4 pm New York price implied by the GLD trust. Each snapshot records the LBMA PM, and the Gold Standard note shows a sensitivity at the LBMA PM (break-evens 0.8 to 1.7 points lower).
- `Risks.holding_cost` (ADR 0049): a real cost per year of deferral beyond the base year, paid by the project. Zero by default, so no published number changes.
- Osino market value at the DFS (#90, ADR 0048). The July 2023 trading range is read on the March 31, 2023 statements: break-even spread 17.0% to 17.9%, against 18.1% for the December undisturbed value. Cash spent to May 29, 2023 is a sensitivity. USD/CAD added to the July 13, 2023 snapshot.
- `Market.flat` for reading a price at a third-party rate (ADR 0045); `pricedin.defaults` reads stage odds, overrun, equity financing and base timing from the priors registry by id, and gives no default stage odds for a PEA-stage case. `pricedin.sensitivity.delay_threshold` reports where delay stops adding project value (ADR 0046).
- Input validation in `Market`, `Timing`, `RoyaltyClaim` and `StreamClaim`; a case template that matches the schema, with a test that loads a filled template; economic sanity tests; CI runs the app test.
- Sum-of-parts adapter (#75, ADR 0044): `pricedin.sum_of_parts` (producing-asset value at the expected gold price, residual band, treasury method); Orla Mining at August 12, 2022 in `data/sum_of_parts/orla_2022-08-12.yaml`, `scripts/orla_sum_of_parts.py` and `docs/cases/orla_sum_of_parts.md`; market snapshot for 2022-08-12.
- Gold Standard Ventures takeover case (#81, ADR 0043): `cases/south_railroad_fs2022.yaml` (the 2022 feasibility study, Table 22-7), market snapshot for 2022-06-10, `scripts/gsv_takeover.py` and the write-up `docs/cases/gold_standard_takeover.md`. Schedule-mode cases can now use mid-year discounting (`project.period_times`). New timing prior `timing.years_to_start.south_railroad_fs2022`.
- Schwartz-Smith two-factor model (#77, ADR 0042): `pricedin.schwartz_smith` with futures pricing, exact state transition, Kalman-filter likelihood and maximum-likelihood fitting; synthetic-recovery test. SciPy added as a dependency. Phase 3 exit amended (ADR 0042).
- Gold streams (#80, ADR 0041): `engine.StreamClaim` and `Results.stream_value` (delivered ounces worth max(P - c, 0), a strip of calls) and `inversion.stream_frontier`; tests against the Black-Scholes strip and synthetic recovery. Methodology updated for Phase 3.
- Brennan and Schwartz (1985) replication (#76, ADR 0040): `pricedin.switching` values a mine with options to close, reopen and abandon by least-squares Monte Carlo with discrete inventory states and a spline basis; every published value is matched within one standard error (`scripts/brennan_schwartz.py`, `data/benchmarks/brennan_schwartz_1985.yaml`).
- Order-independent waterfall (#79, ADR 0039): `report.shapley_waterfall` gives each risk step its Shapley value over the four risks, with path-level standard errors; Osino note and `scripts/osino_case.py` show both versions.
- Optimal build timing (#76, ADR 0038): `Risks(build_decision="lsm")` builds when the market-consistent value of building now is at least the fitted value of waiting, fitted on independent paths; `lsm_rate` sets the decision rate. The fixed rule stays the headline; `scripts/build_rule_comparison.py` compares the two for Osino and South Railroad, and the case notes report the comparison.
- Least-squares Monte Carlo core (#76, ADR 0037): `pricedin.lsm` (Longstaff and Schwartz 2001), validated on the American put against QuantLib; QuantLib added as the `validation` dependency group. Accepts a one-step discount factor above 1 (negative real rates).

## [0.2.0] - 2026-11-16

Phase 2: price adapters, inversion and the public back-test.

### Added
- Back-test write-up (#74): `docs/backtest.md`, and `scripts/backtest.py`, which regenerates every number in it.
- Multi-metal royalty cases (#72, ADR 0036): `pricedin.royalty_cases` (closed-form market-consistent royalty value on a multi-metal study table, correlated Monte Carlo check, implied odds of reaching production, break-even spread) and `price_models.CorrelatedGBM`.
- Sorby Hills royalty case (ADR 0035): `cases/sorby_hills.yaml` (FEED Table 10), market snapshot for 2026-09-28, `scripts/sorby_hills_case.py` and the write-up `docs/cases/sorby_hills.md`. The price equals the on-schedule value at a 2.3% real spread.
- Royalty transaction dataset (#73): `data/transactions.csv` with its loader and checks (`pricedin.transactions`). Six disclosed deals: South Railroad (modelled), Sorby Hills (modelled), the Wharf control, and three deals listed but out of scope with the reason stated (White Dam, Kalman and Sylvania, and the February 2026 Australian portfolio).
- ADR 0033: Osino corporate G&A and the fairness-opinion reference band. Osino prices re-run on Osino's own September 30, 2023 statements, with the December 15, 2023 undisturbed value as headline (`scripts/osino_prices.py`, replacing `scripts/osino_bids.py`).
- ADR 0032: Osino bids shown against a project-level spread with the break-even marked; provisional bid section in the Osino write-up and `scripts/osino_bids.py`.
- ADR 0031: Osino takeover and developer adapters. Market snapshots for 2023-12-15, 2023-12-18 and 2024-02-23.
- `inversion.equity_frontier`: implied gate odds from an equity-based price (developer and takeover adapters), with synthetic recovery test.

### Fixed
- The Shanjin price used a December 31, 2023 balance published after the price date; replaced with the September 30, 2023 statements.

## [0.1.0] - 2026-11-16

First release: the Phase 1 forward engine on two public cases, and the South Railroad royalty inversion pulled forward from Phase 2.

### Added
- App (#65): `app/streamlit_app.py` with valuation, royalty price, timing and assumptions views; optional extra `app` (`uv sync --extra app`). Smoke test runs both cases when Streamlit is installed.
- Sensitivities and readout (#63): `pricedin.sensitivity` (tornado, build-year distribution, template readout). Osino Twin Hills forward valuation write-up (`docs/cases/osino_twin_hills.md`) and `scripts/osino_case.py` (#64).
- Equity claim (#61, ADR 0030): `engine.Financing` and `Results.equity_value`; priors `equity.issue_discount` (Carpentier and Suret 2009) and `equity.debt_fraction`. ADR 0029: ramp-up not modelled in the public cases.
- ADR 0028: South Railroad presented as an illustration across the buyer's spread, with the Osisko impairment rate and the Wharf control as reference points. `inversion.break_even_spread`, `zero_delay_value`, `zero_delay_odds_curve`. Case write-up `docs/cases/south_railroad.md` and `scripts/south_railroad_case.py`.
- Waterfall (#62): `pricedin.report.project_waterfall` steps from the study NPV through discounting, market prices, base timing, overrun, ramp-up (labelled not modelled), stage failure, and price uncertainty with the build decision, on common paths. Steps sum exactly to the total.
- Producing-royalty controls (`pricedin.controls`): implied real spread in market-consistent mode, analyst-mode implied rate, Tier 2 schedules from reserves and rate. First control file `controls/wharf.yaml` (Metalla, 2020), all values sourced. ADR 0027: the futures check is replaced by the same-y gold-control condition.
- ADR 0026: control criteria amended (share consideration at closing-date fair value; two-tier mine-plan test; one-control rule).
- Inversion (#71): `pricedin.inversion.royalty_frontier` solves implied gate odds for each added delay in closed form (value is linear in the odds), with Monte Carlo standard errors, a noise-aware shape test, the zero-delay odds and the certain-build delay. Synthetic recovery tests. ADR 0025: failing paths fail at the base build-ready year; `Timing.failure_after_delay` keeps the old rule as a sensitivity.
- ADR 0024: market inputs. `Market.from_snapshot`, prior `market.convenience_yield.gold`, Bank of Canada 10-year yield in the 2021 snapshot, and `engine.fixed_nominal_advance` (covered interest parity valuation of the fixed C$ advances). Test that the royalty value is independent of the real rate in market-consistent mode.
- Market snapshots (`pricedin.snapshots`, `data/snapshots/2021-06-07.yaml`, `2023-07-13.yaml`): gold spot, TIPS real yields (5, 7, 10 years), 10-year breakeven, USD/CAD, GVZ and realised volatility, each with source, series, observation date and status; observations after the valuation date are rejected. `scripts/realised_vol.py` reproduces the realised volatility figures.
- Advance minimum royalties as a fixed nominal amount (ADR 0021): `RoyaltyClaim.amr_inflation` deflates each advance to real terms, and credited advances are recovered as the same nominal total.
- ADR 0023: base timing per case (South Railroad 4 years from CEQ BLM EIS data; Osino 1 year from DFS guidance), no timing prior for the reported point, build hurdle and 5-year window. Priors `timing.years_to_start.*`, `build.hurdle`, `build.window_years`; registry status `J` for stated judgments. Engine: `Risks.decision_rate`, and `Results.window_expired_share` and `advance_share` diagnostics.
- Simulation engine (#57 to #59, part of 1.8): `pricedin.engine.simulate` draws gold paths, stage gates, the capital cost ratio and the build year, and values the project and a royalty with advance minimum royalties on the same paths. Every risk has a switch; with all off the engine returns the study NPV exactly. ADR 0022 records the timing conventions.

### Fixed
- mypy no-any-return on Python 3.11 in `price_models` (#4).

### Added
- ADRs 0018 to 0021: tax approximation; ramp-up by plant class, superseding 0017; royalty price basis, clarifying 0014; advance royalties and buy-down for South Railroad. Oxide-class ramp-up weights (`rampup.weight.oxide.*`).
- Schedule-mode project cash flow (#56): `pricedin.project` recomputes revenue, revenue-linked costs and tax for any gold price path; reproduces both study tables exactly at the deck and the published price sensitivities within the errors in ADR 0018. Cases gain `gold_revenue`, `revenue_linked` and a sourced `marginal_tax_rate`.
- McNulty (1998) ramp-up curves digitised from the original Figure 1 (`data/ramp_up_mcnulty_1998.csv`) and series weights from its Table 2 (`rampup.weight.series1` to `series4`).
- Osino Twin Hills case (`cases/osino_twin_hills.yaml`) from DFS Table 22.3.2, reproducing the published NPV5 within cell rounding; two internal DFS inconsistencies documented.

### Changed
- Case schema: money units declared once per case (`schedule.money_units`, US$ thousands or millions); NPV fields renamed `npv_pre_tax` and `npv_after_tax`; per-row `resolution` for total checks.

### Added (earlier)
- Vox South Railroad terms from Vox's audited statements and AIF recorded in `docs/sources.md`; project state updated.
- ADRs 0015 (PFS overrun), 0016 (South Railroad royalty coverage) and 0017 (ramp-up in schedule mode); `capex.overrun.pfs` prior with its flag and a mean-preserving sensitivity.
- Gold price model (#55): `pricedin.price_models.GBM`, exact-solution annual paths with optional antithetic draws, and `flat_deck` for study-deck reconciliation. Tests check reproducibility, log-return moments, E[S_t] = S_0 e^(drift t), and the 1/sqrt(n) fall in standard error.
- Repository scaffold: `src/` package layout, uv and hatchling packaging, ruff, mypy (strict), pytest with coverage, pre-commit, GitHub Actions CI on Python 3.11 and 3.12.
- Project documents: README, licence, citation file, contributing guide, roadmap, project state, methodology and calibration outlines, sources register.
- Founding decision records 0001 to 0012.
- Decision records 0013 (stage-transition priors) and 0014 (producing-royalty controls; amends 0008).
- Case input template (schedule mode): `pricedin.inputs` schema and loader, `cases/_template.yaml`, and `cases/south_railroad.yaml` transcribed from the 2020 PFS Table 22-7. Every value carries a document and page reference; row totals, the cash-flow identity and the published NPVs (pre-tax and after-tax, 5%) are reproduced in tests. Documents dated after the valuation date are rejected.
- Priors registry: `data/priors.yaml` and a validating loader in `pricedin.priors`. Entries without a source, location, units or status are rejected; secondary-source entries must carry a flag. First entries: `stage.pfs_to_fs`, `stage.fs_to_build`.
