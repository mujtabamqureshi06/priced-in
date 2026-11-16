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
| [Osino Twin Hills](docs/cases/osino_twin_hills.md) (Namibia, DFS, July 2023) | DFS NPV US$480M at 5% and US$1,750/oz | US$899M under market prices on the DFS date; stage odds and the gold convenience yield move it most |
| [Osino Twin Hills](docs/cases/osino_twin_hills.md), prices | Undisturbed market value (Dec 2023), Dundee and Shanjin offers | At the fairness opinion's 10.5% to 13.5% real rates, odds of roughly 0.4 to 0.6 that the project is built on schedule |
| [South Railroad](docs/cases/south_railroad.md) (Nevada, PFS, June 2021) | Vox Royalty paid US$2.079M for a 0.633% NSR | The implied odds depend mainly on the return the buyer required: about 0.7 to 0.8 on schedule at a royalty company's own valuation rate; at the one qualifying market control, the PFS plan alone cannot account for the price |
| [Sorby Hills](docs/cases/sorby_hills.md) (Western Australia, silver-lead, in construction, Sept 2026) | Vox Royalty agreed to pay US$13.0M for an effective 0.75% NSR | The price equals the value of the study mine plan built on time at a 2.3% real spread: consistent with near-certain completion at royalty-company rates |

The [Phase 2 back-test](docs/backtest.md) reads these cases together. Its main finding is that the required return dominates every answer.

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
from pricedin.engine import Market, Risks, Timing, simulate
from pricedin.inputs import load_case
from pricedin.snapshots import load_snapshot

case = load_case(Path("cases/osino_twin_hills.yaml"))
snap = load_snapshot(Path("data/snapshots/2023-07-13.yaml"))
market = Market.from_snapshot(snap, convenience_yield=0.0)
res = simulate(
    case,
    market,
    Timing(years_to_start=1, max_wait=5),
    Risks(stage_odds=0.88, build_rule=True),
    n_paths=10_000,
    seed=1,
)
print(res.estimate(res.project_value))  # (mean, Monte Carlo standard error), US$ million
```

The app is live at [priced-in.streamlit.app](https://priced-in.streamlit.app/). To run it locally: `uv sync --extra app` then `uv run streamlit run app/streamlit_app.py`. Every number in the back-test: `uv run python scripts/backtest.py`.

## Repository layout

| Path | Contents |
|---|---|
| `src/pricedin/` | Engine: inputs, priors, price models, project cash flow, simulation, inversion, controls, multi-metal royalty cases, transaction dataset, waterfall, sensitivities |
| `cases/` | Study cash-flow tables transcribed with page references |
| `controls/` | Producing-royalty purchases used to calibrate the buyer's required return |
| `data/` | Priors registry, market snapshots, royalty transaction dataset, digitised ramp-up curves |
| `docs/` | Methodology, calibration, sources register, case write-ups, decision records, project state |
| `scripts/`, `app/` | Reproducible case tables and the Streamlit app |

## Status

Phases 1 (forward engine) and 2 (price adapters, inversion and the public back-test) are complete; ramp-up is not modelled because the public studies do not give enough detail (ADR 0029). Phase 3 (Longstaff-Schwartz build decision, multi-asset and multi-metal projects) is next. See [docs/ROADMAP.md](docs/ROADMAP.md) and [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md).

## Development

Conventions are in [CONTRIBUTING.md](CONTRIBUTING.md): type hints throughout (mypy strict), ruff, pytest with coverage, CI on Python 3.11 and 3.12, one pull request per change, decisions recorded as ADRs.

## Licence

Code: MIT ([LICENSE](LICENSE)). The compiled dataset, when published: CC BY 4.0. Third-party documents (technical reports, papers, filings) are never redistributed; the repository holds links and page references only.
