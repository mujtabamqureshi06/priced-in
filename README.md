# Priced In

Priced In values a mine that has not been built yet, compares that value to what people actually pay for it, and reports the build odds and timing the price implies.

## The problem

The technical-report NPV of an undeveloped mine is usually far above what the market pays for it. Analysts close the gap with a single risking multiple (P/NAV). The multiple does not say how much of the discount reflects the chance the mine is never built, how much reflects delay, and how much reflects cost overruns or dilution.

## What Priced In does

1. **Forward engine.** Takes structured inputs from a technical report and simulates the project many times: gold price paths, study and permitting gates, capex overrun, delay, ramp-up and the build decision. Cash flows are priced consistently with their risk (Samis et al. 2006); the engine does not report a distribution of NPVs discounted at a risk-adjusted rate (Davis 1995).
2. **Claims.** From the same simulated paths it values the whole project, the operator's equity after dilution, and any royalty or stream.
3. **Price comparison.** Given an observed price (a royalty purchase, a developer's enterprise value or a takeover offer), it backs out the combinations of build probability and timing consistent with that price. One price cannot separate the two, so the output is a frontier plus a point estimate under a stated timing prior.
4. **Waterfall.** It splits the gap between the study NPV and the price into named pieces: delay, overrun, stage risk, dilution, price effects and an unexplained residual.

## What it does not claim

It does not claim the market is wrong, that DCF is broken, or that its output is a trading signal. It states what a price implies, in pieces that can be argued with.

## Status

Phase 0 (foundation). No modelling code yet. See [docs/ROADMAP.md](docs/ROADMAP.md) and [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md).

## Development

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11 or later.

```bash
uv sync --all-groups
uv run pre-commit install
uv run pytest
```

Conventions are in [CONTRIBUTING.md](CONTRIBUTING.md). Design decisions are recorded in [docs/decisions/](docs/decisions/).

## Licence

Code: MIT ([LICENSE](LICENSE)). The compiled dataset, when published: CC BY 4.0. Third-party documents (technical reports, papers, filings) are never redistributed; the repository holds links and page references only.
