# Priced In

Priced In values a mine that has not been built yet, compares that value to what people actually pay for it, and reports the build odds and timing the price implies.

## The problem

The technical-report NPV of an undeveloped mine is usually far above what the market pays for it. Analysts close the gap with a single risking multiple (P/NAV). The multiple does not say how much of the discount reflects the chance the mine is never built, how much reflects delay, and how much reflects cost overruns or dilution.

## What it does

1. **Forward engine.** Takes a study's own cash-flow table and simulates the project many times: gold price paths, stage gates, capital overrun, delay and a price-dependent build decision. Cash flows are priced consistently with their risk (market-consistent mode: risk-neutral gold, real risk-free discounting, project risks at real-world odds). It never reports a distribution of NPVs discounted at a risk-adjusted rate.
2. **Claims.** From the same simulated paths it values the whole project, the operator's equity after dilution, and a royalty, including advance minimum payments.
3. **Inversion.** Given a price, it solves for the build odds consistent with that price at each possible delay. One price cannot separate odds from timing, so the output is a frontier, summarised by the lowest odds consistent with the price on schedule and the delay at which the price would mean certain construction.
4. **Waterfall and sensitivities.** It splits the gap between the study NPV and the engine's value into named steps, and ranks the inputs that move the answer most.

With all risks off, the study's flat price deck and its discount rate, the engine reproduces each study's cash-flow table and NPV exactly. This is tested.

## Results so far

| Case | Price or study | What the engine says |
|---|---|---|
| [Osino Twin Hills](docs/cases/osino_twin_hills.md) (Namibia, DFS, July 2023) | DFS NPV US$480M at 5% and US$1,750/oz | US$908M (standard error 1.8) under market prices on the DFS date; stage odds and the gold convenience yield move it most |
| [Osino Twin Hills](docs/cases/osino_twin_hills.md), prices | Market value at the DFS (July 2023), undisturbed market value (Dec 2023), Dundee and Shanjin offers | At the fairness opinion's 10.5% to 13.5% real rates and its US$1,850 gold deck, odds of roughly 0.6 to 1 that the project is built on schedule (about 0.5 to 0.85 at spot gold). The July and December market values need almost the same project-level spread, about 17% to 18%, to be fair |
| [South Railroad](docs/cases/south_railroad.md) (Nevada, PFS, June 2021) | Vox Royalty paid US$2.079M for a 0.633% NSR | The implied odds depend mainly on the return the buyer required: about 0.8 to 0.9 on schedule at a royalty company's own valuation rate and gold deck (about 0.65 to 0.75 at spot gold); at the one qualifying market control, the PFS plan alone cannot account for the price |
| [Gold Standard Ventures](docs/cases/gold_standard_takeover.md) (Nevada, FS, June 2022) | Orla Mining offered C$0.655 a share (C$242M gross) for Gold Standard, owner of South Railroad | At the FS's base 5% rate and its US$1,650 gold deck, the offer is consistent with odds of about 0.65 to 0.75 that South Railroad is built, depending on whether permitting takes the BLM median or the company schedule |
| [Orla Mining](docs/cases/orla_sum_of_parts.md), sum of parts (Aug 2022) | Orla's market value after closing the Gold Standard acquisition | Orla traded well above the sum of its published plans, so the residual for South Railroad is an upper bound and does not identify its odds |
| [Sorby Hills](docs/cases/sorby_hills.md) (Western Australia, silver-lead, in construction, Sept 2026) | Vox Royalty agreed to pay US$13.0M for an effective 0.75% NSR | Assuming the royalty covers silver and lead (an inference; Vox calls it a silver royalty), the price equals the value of the study plan built on time at a 2.3% market-consistent spread. At a royalty company's own rate and deck the price is above that value, so no odds reconcile it |

The [back-test](docs/backtest.md) reads these cases together. Its main finding is that the required return dominates every answer. Published values use 200,000 simulated paths; standard errors are shown in the case notes.

Reference rates published by others (royalty-company impairment tests, fairness opinions, study rates) are applied the way their sources applied them, with the source's own price deck ([ADR 0045](docs/decisions/0045-reference-rate-convention.md)). An earlier version converted them to spreads incorrectly; the [changelog](CHANGELOG.md) lists the corrected values.

One behaviour to keep in mind: with a zero gold convenience yield, expected gold grows at the real interest rate while costs are fixed, so delaying construction can raise a project's value ([ADR 0046](docs/decisions/0046-delay-at-zero-convenience-yield.md)).

Every input carries its source and verification status in [data/priors.yaml](data/priors.yaml), [data/snapshots/](data/snapshots/) and the case files. Every judgment is a decision record in [docs/decisions/](docs/decisions/).

## What it does not claim

It does not claim the market is wrong, that DCF is broken, or that its output is a trading signal. It states what a price implies, in pieces that can be argued with. Results on real deals never say that a buyer overpaid or a seller was wrong.

## Quick start

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11 or later.

```bash
uv sync --all-groups
uv run pytest
uv run python scripts/osino_case.py          # Osino tables
uv run python scripts/south_railroad_case.py # South Railroad tables
```

```python
from pathlib import Path
from pricedin import defaults
from pricedin.engine import Market, Risks, simulate
from pricedin.inputs import load_case
from pricedin.priors import load_priors
from pricedin.snapshots import load_snapshot

case = load_case(Path("cases/osino_twin_hills.yaml"))
snap = load_snapshot(Path("data/snapshots/2023-07-13.yaml"))
market = Market.from_snapshot(snap, convenience_yield=0.0)
priors = load_priors(Path("data/priors.yaml"))
res = simulate(
    case,
    market,
    defaults.timing(priors, case.id),
    Risks(
        stage_odds=defaults.stage_odds(priors, case.study.stage),
        overrun=defaults.overrun(priors, case.study.stage),
        build_rule=True,
    ),
    n_paths=200_000,
    seed=1,
)
print(res.estimate(res.project_value))  # (908.2, 1.8): mean and standard error, US$ million
```

The app is live at [priced-in.streamlit.app](https://priced-in.streamlit.app/). To run it locally: `uv sync --extra app` then `uv run streamlit run app/streamlit_app.py`. Every number in the back-test: `uv run python scripts/backtest.py`.

Market snapshots (`data/snapshots/`) hold derived values only. Gold volatilities come from a vendor's daily gold prices (Alpha Vantage), which are not redistributed; `scripts/realised_vol.py` recomputes a snapshot volatility from a downloaded copy of that series.

## Repository layout

| Path | Contents |
|---|---|
| `src/pricedin/` | `inputs`, `priors`, `defaults` (settings read from the priors registry), `price_models`, `schwartz_smith` (two-factor model and Kalman filter), `project` (cash flow), `engine` (simulation and claims), `lsm` (least-squares Monte Carlo), `switching` (Brennan-Schwartz mine), `inversion`, `controls`, `royalty_cases` (multi-metal royalties), `sum_of_parts`, `transactions`, `report` (waterfalls), `sensitivity` |
| `cases/` | Study cash-flow tables transcribed with page references, and the input template |
| `controls/` | Producing-royalty purchases used to calibrate the buyer's required return |
| `data/` | Priors registry, market snapshots, royalty transaction dataset, sum-of-parts inputs, benchmark values, digitised ramp-up curves |
| `docs/` | Methodology, calibration, sources register, case write-ups, back-test, decision records, roadmap |
| `scripts/`, `app/` | Reproducible case tables and the Streamlit app |

## Status

Phases 1 to 3 are complete and released (v0.1.0, v0.2.0, v1.0.0). Phase 3 added the least-squares Monte Carlo build decision (checked against QuantLib and a replication of Brennan and Schwartz 1985), the order-independent waterfall, gold streams, the Schwartz-Smith two-factor model, the Gold Standard takeover and the Orla sum of parts. Calibration to copper futures and a uranium deck are deferred (ADR 0042). Ramp-up is not modelled because the public studies do not give enough detail (ADR 0029). Phase 4, a test of whether implied odds carry information about which projects get built, is in progress; nothing here claims predictive power. See [docs/ROADMAP.md](docs/ROADMAP.md) and [CHANGELOG.md](CHANGELOG.md).

## How this was built

I designed this project and made or approved every modelling choice; each is recorded with its reasons in [docs/decisions/](docs/decisions/). I used AI assistants (Anthropic's Claude) to research sources, write and test code, and draft documents, under my direction and review. The commit history shows this: some commits carry co-author lines from those tools. Every number traces to a source or a script in this repository, and the tests check the engine against published results.

## Development

Conventions are in [CONTRIBUTING.md](CONTRIBUTING.md): type hints throughout (mypy strict), ruff, pytest with coverage, CI on Python 3.11 and 3.12, one pull request per change, decisions recorded as ADRs.

## Licence

Code: MIT ([LICENSE](LICENSE)). The compiled dataset, when published: CC BY 4.0. Third-party documents (technical reports, papers, filings) are never redistributed; the repository holds links and page references only.
