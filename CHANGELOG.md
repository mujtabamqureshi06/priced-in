# Changelog

All notable changes are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- ADR 0024 (Decision Maker, DR-010): market inputs. `Market.from_snapshot`, prior `market.convenience_yield.gold`, Bank of Canada 10-year yield in the 2021 snapshot, and `engine.fixed_nominal_advance` (covered interest parity valuation of the fixed C$ advances). Test that the royalty value is independent of the real rate in market-consistent mode.
- Market snapshots (`pricedin.snapshots`, `data/snapshots/2021-06-07.yaml`, `2023-07-13.yaml`): gold spot, TIPS real yields (5, 7, 10 years), 10-year breakeven, USD/CAD, GVZ and realised volatility, each with source, series, observation date and status; observations after the valuation date are rejected. `scripts/realised_vol.py` reproduces the realised volatility figures.
- Advance minimum royalties as a fixed nominal amount (ADR 0021): `RoyaltyClaim.amr_inflation` deflates each advance to real terms, and credited advances are recovered as the same nominal total.
- ADR 0023 (Decision Maker, DR-009): base timing per case (South Railroad 4 years from CEQ BLM EIS data; Osino 1 year from DFS guidance), no timing prior for the reported point, build hurdle and 5-year window. Priors `timing.years_to_start.*`, `build.hurdle`, `build.window_years`; registry status `J` for stated judgments. Engine: `Risks.decision_rate`, and `Results.window_expired_share` and `advance_share` diagnostics.
- Simulation engine (WP 1.4 to 1.6, part of 1.8): `pricedin.engine.simulate` draws gold paths, stage gates, the capital cost ratio and the build year, and values the project and a royalty with advance minimum royalties on the same paths. Every risk has a switch; with all off the engine returns the study NPV exactly. ADR 0022 records the timing conventions.

### Fixed
- mypy no-any-return on Python 3.11 in `price_models` (#4).

### Added
- ADRs 0018 to 0021: tax approximation (Mastermind); ramp-up by plant class, superseding 0017; royalty price basis, clarifying 0014; advance royalties and buy-down for South Railroad. Oxide-class ramp-up weights (`rampup.weight.oxide.*`).
- Schedule-mode project cash flow (WP 1.3): `pricedin.project` recomputes revenue, revenue-linked costs and tax for any gold price path; reproduces both study tables exactly at the deck and the published price sensitivities within the errors in ADR 0018. Cases gain `gold_revenue`, `revenue_linked` and a sourced `marginal_tax_rate`.
- McNulty (1998) ramp-up curves digitised from the original Figure 1 (`data/ramp_up_mcnulty_1998.csv`) and series weights from its Table 2 (`rampup.weight.series1` to `series4`).
- Osino Twin Hills case (`cases/osino_twin_hills.yaml`) from DFS Table 22.3.2, reproducing the published NPV5 within cell rounding; two internal DFS inconsistencies documented.

### Changed
- Case schema: money units declared once per case (`schedule.money_units`, US$ thousands or millions); NPV fields renamed `npv_pre_tax` and `npv_after_tax`; per-row `resolution` for total checks.

### Added (earlier)
- Vox South Railroad terms from Vox's audited statements and AIF recorded in `docs/sources.md`; project state updated.
- ADRs 0015 (PFS overrun), 0016 (South Railroad royalty coverage) and 0017 (ramp-up in schedule mode), from Decision Maker records DR-003 to DR-005; `capex.overrun.pfs` prior with its flag and a mean-preserving sensitivity.
- Gold price model (WP 1.2): `pricedin.price_models.GBM`, exact-solution annual paths with optional antithetic draws, and `flat_deck` for study-deck reconciliation. Tests check reproducibility, log-return moments, E[S_t] = S_0 e^(drift t), and the 1/sqrt(n) fall in standard error.
- Repository scaffold: `src/` package layout, uv and hatchling packaging, ruff, mypy (strict), pytest with coverage, pre-commit, GitHub Actions CI on Python 3.11 and 3.12.
- Project documents: README, licence, citation file, contributing guide, roadmap, project state, methodology and calibration outlines, sources register.
- Founding decision records 0001 to 0012.
- Decision records 0013 (stage-transition priors) and 0014 (producing-royalty controls; amends 0008), made by the Independent Decision Maker.
- Case input template (schedule mode): `pricedin.inputs` schema and loader, `cases/_template.yaml`, and `cases/south_railroad.yaml` transcribed from the 2020 PFS Table 22-7. Every value carries a document and page reference; row totals, the cash-flow identity and the published NPVs (pre-tax and after-tax, 5%) are reproduced in tests. Documents dated after the valuation date are rejected.
- Priors registry: `data/priors.yaml` and a validating loader in `pricedin.priors`. Entries without a source, location, units or status are rejected; secondary-source entries must carry a flag. First entries: `stage.pfs_to_fs`, `stage.fs_to_build`.
