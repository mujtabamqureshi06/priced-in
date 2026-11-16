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
| [South Railroad](docs/cases/south_railroad.md) (Nevada, PFS, June 2021) | Vox Royalty paid US$2.079M for a 0.633% NSR | The implied odds depend mainly on the return the buyer required: about 0.7 to 0.8 on schedule at a royalty company's own valuation rate; at the one qualifying market control, the PFS plan alone cannot account for the price |

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

The app: `uv sync --extra app` then `uv run streamlit run app/streamlit_app.py`. Deployment: [docs/deploying_the_app.md](docs/deploying_the_app.md).

## Repository layout

| Path | Contents |
|---|---|
| `src/pricedin/` | Engine: inputs, priors, price model, project cash flow, simulation, inversion, controls, waterfall, sensitivities |
| `cases/` | Study cash-flow tables transcribed with page references |
| `controls/` | Producing-royalty purchases used to calibrate the buyer's required return |
| `data/` | Priors registry, market snapshots, digitised ramp-up curves |
| `docs/` | Methodology, calibration, sources register, case write-ups, decision records, project state |
| `scripts/`, `app/` | Reproducible case tables and the Streamlit app |

## Status

Phase 1 (forward engine) is complete apart from ramp-up, which the public studies do not give enough detail to model (ADR 0029). The South Railroad royalty inversion from Phase 2 is done; the developer and takeover adapters are next. See [docs/ROADMAP.md](docs/ROADMAP.md) and [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md).

## Development

Conventions are in [CONTRIBUTING.md](CONTRIBUTING.md): type hints throughout (mypy strict), ruff, pytest with coverage, CI on Python 3.11 and 3.12, one pull request per change, decisions recorded as ADRs.

## Licence

Code: MIT ([LICENSE](LICENSE)). The compiled dataset, when published: CC BY 4.0. Third-party documents (technical reports, papers, filings) are never redistributed; the repository holds links and page references only.
