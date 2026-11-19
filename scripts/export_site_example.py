"""Export the illustrative mine shown on the website's home page.

The mine is made up to show the method. Every figure the home page displays comes
from this script: the engine values the mine on the inputs below and the results are
written to ``site/data/example.json``. The page builder (``site/build.py``) only reads
that file, so no number on the page is typed by hand.

What is exported:

- ``grid``: project value if built, its standard error and the share of paths built,
  for each gold price today (US$1,800, 2,000, 2,200 an ounce), each extra return over
  the real risk-free rate (6% to 15%) and with or without capital overruns.
- ``tornado``: project value at a 10% extra return when one input moves.
- ``bridge``: study NPV, then the market-consistent value without and with overruns,
  then the value at a 10% extra return.
- ``cf``: the study's after-tax cash flow by year, as calibrated.
- ``paths`` and ``q``: the first 40 simulated gold price paths over 12 years, and the
  5th, 50th and 95th percentiles across all paths. These are the engine's own price
  draws for the base run, not a separate simulation.
- ``overrun_hist``: the capital cost ratios drawn in the base run, in real terms.
- ``odds``: implied odds of a build on schedule for every control state (price paid,
  gold, extra return, overruns), and ``value_m``, the value if built rounded to a whole
  US$ million. Odds are price over that displayed value, as a whole percent rounded half
  up, so the division shown on the page checks exactly; ``null`` when the price is above
  the value (no odds are high enough). The simulation error on the value (``se_max``) is
  larger than the effect of rounding it.
- ``gold_figures``: the middle path and the 5th to 95th percentile range after 12 years,
  for each gold price.
- ``gate_draws``: the engine's uniform stage-gate draw for each drawn price path. The
  page draws a path in gold when its draw is below the implied odds, so the gold lines
  are the outcomes that pass at those odds.
- ``sensitivity``: the implied odds at the starting settings when one input moves.

Usage: uv run python scripts/export_site_example.py [--out site/data/example.json]
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
import subprocess
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np

from pricedin import defaults
from pricedin.engine import Market, Overrun, Risks, Timing, simulate
from pricedin.parametric import Headline, build_case, calibrate
from pricedin.price_models import GBM
from pricedin.priors import load_priors

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "site" / "data" / "example.json"

N_PATHS, SEED = 200_000, 1
SCHEMA_VERSION = 1

# The illustrative mine: a two-year build, ten years of production, after-tax NPV of
# US$250M at 5% and IRR of 20% on a flat US$1,800 gold deck. Money in US$ millions.
STUDY_NPV = 250.0
HEADLINE = Headline(
    initial_capex=300.0,
    preproduction_years=2,
    life_years=10,
    payable_koz_per_year=120.0,
    aisc_per_oz=1000.0,
    gold_deck=1800.0,
    tax_rate=0.25,
    discount_rate=0.05,
    npv_after_tax=STUDY_NPV,
    irr_after_tax=0.20,
)

# Market: gold today, the real risk-free rate and gold volatility (all illustrative).
SPOT, REAL_RATE, VOLATILITY = 2000.0, 0.015, 0.15
TIMING = Timing(years_to_start=1, max_wait=5)

GOLDS = (1800.0, 2000.0, 2200.0)
EXTRA_RETURNS = (0.06, 0.08, 0.10, 0.12, 0.15)
BASE_RETURN = 0.10
FAN_PATHS, FAN_YEARS = 40, 12
HIST_EDGES = tuple(round(0.8 + 0.1 * k, 1) for k in range(13))  # 0.8 to 2.0
PRICES = (80, 120, 160, 200)  # price paid on the page's control, US$M
BASE_PRICE = 120


def whole(x: float) -> int:
    """Round half up to a whole number (the page's rounding rule for every figure)."""
    return math.floor(x + 0.5)


def implied_odds(price: float, value: float) -> int | None:
    """Implied odds of a build on schedule, whole percent; None if no odds are high enough.

    If the mine is never built the buyer receives nothing, so a price equals the odds
    times the value if built. The odds are therefore price over value. The value is
    first rounded to the whole US$ million the page shows, so the page's division checks.
    """
    shown = whole(value)
    if shown <= 0 or price > shown:
        return None
    return whole(100 * price / shown)


def _commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return out.stdout.strip()


def _case() -> Any:
    return build_case(
        HEADLINE,
        case_id="example_mine",
        name="Example mine",
        operator="Example",
        jurisdiction="Example",
        as_of=date(2026, 1, 1),
        stage="FS",
        document_title="Illustrative mine (made up)",
        document_url="https://github.com/mujtabamqureshi06/priced-in",
        document_date=date(2026, 1, 1),
        location="illustrative",
    )


def _market(spot: float, extra_return: float, volatility: float) -> Market:
    m = Market.market_consistent(spot, REAL_RATE, 0.0, volatility)
    return replace(m, discount_rate=REAL_RATE + extra_return)


class _Runner:
    """Runs the engine on the illustrative mine with one set of base inputs."""

    def __init__(self, n_paths: int, seed: int) -> None:
        priors = load_priors(ROOT / "data" / "priors.yaml")
        self.case = _case()
        self.overrun: Overrun = defaults.overrun(priors, "FS")
        self.n_paths, self.seed = n_paths, seed

    def value(
        self,
        extra_return: float,
        *,
        spot: float = SPOT,
        volatility: float = VOLATILITY,
        overrun: bool = True,
        delay: int = 0,
    ) -> tuple[float, float, float]:
        """Project value if built (US$M), its standard error, and the share built."""
        risks = Risks(stage_odds=1.0, overrun=self.overrun if overrun else None, build_rule=True)
        timing = replace(TIMING, added_delay=delay)
        r = simulate(
            self.case,
            _market(spot, extra_return, volatility),
            timing,
            risks,
            n_paths=self.n_paths,
            seed=self.seed,
        )
        v, se = r.estimate(r.project_value)
        return float(v), float(se), float(r.built.mean())

    def study_check(self) -> float:
        """Study-deck NPV with every risk off; reproduces the headline NPV."""
        r = simulate(self.case, Market.study_deck(self.case), Timing(), Risks(), n_paths=10, seed=1)
        return float(r.project_value.mean())

    def price_paths(self) -> np.ndarray:
        """Return the gold price paths of the base run (same seed stream as the engine)."""
        m = _market(SPOT, BASE_RETURN, VOLATILITY)
        horizon = TIMING.build_ready + TIMING.max_wait + len(self.case.schedule.periods)
        price_rng = np.random.default_rng(np.random.SeedSequence(self.seed).spawn(4)[0])
        prices = GBM(m.gold_spot, m.drift, m.volatility).simulate(horizon, self.n_paths, price_rng)
        return np.asarray(prices)[:, : FAN_YEARS + 1]

    def gate_draws(self) -> np.ndarray:
        """Return the uniform stage-gate draws of the base run (same seed stream as the engine)."""
        gate_rng = np.random.default_rng(np.random.SeedSequence(self.seed).spawn(4)[1])
        return gate_rng.random(self.n_paths)

    def overrun_ratios(self) -> np.ndarray:
        """Return the real capital cost ratios drawn in the base run (engine seed stream)."""
        rng = np.random.default_rng(np.random.SeedSequence(self.seed).spawn(4)[2])
        dist = self.overrun.ratio
        lognormal = np.exp(rng.normal(dist.mu, dist.sigma, self.n_paths))
        return self.overrun.real_factor * (dist.shift + lognormal)


def _hist(ratios: np.ndarray) -> dict[str, Any]:
    """Share of draws (%) in each 0.1-wide bin from 0.8; the last bin is 2.0 and above."""
    edges = np.asarray(HIST_EDGES)
    idx = np.clip(np.searchsorted(edges, ratios, side="right") - 1, 0, len(edges) - 1)
    counts = np.bincount(idx, minlength=len(edges))
    share = counts / len(ratios) * 100
    return {
        "edges": list(HIST_EDGES),
        "share": [round(float(s), 1) for s in share],
        "mean": round(float(ratios.mean()), 4),
        "median": round(float(np.median(ratios)), 4),
        "over2": round(float((ratios >= 2.0).mean()), 4),
        "min": round(float(ratios.min()), 4),
    }


def export(n_paths: int = N_PATHS, seed: int = SEED) -> dict[str, Any]:
    """Run the engine and return the home page data."""
    run = _Runner(n_paths, seed)
    calibration = calibrate(HEADLINE)

    # Values are kept unrounded here; every published figure is rounded once, below.
    grid: dict[str, dict[str, float]] = {}
    for gold in GOLDS:
        for extra in EXTRA_RETURNS:
            for ov in (1, 0):
                v, se, built = run.value(extra, spot=gold, overrun=bool(ov))
                key = f"{int(gold)}_{round(extra * 100)}_{ov}"
                grid[key] = {"v": v, "se": se, "built": built}

    ret = round(BASE_RETURN * 100)
    base_key = f"{int(SPOT)}_{ret}_1"
    bridge = {
        "study": STUDY_NPV,
        "market_no_overrun": run.value(0.0, overrun=False)[0],
        "market_overrun": run.value(0.0)[0],
        "at_return": grid[base_key]["v"],
    }
    tornado = {
        "gold_minus10": grid[f"1800_{ret}_1"]["v"],
        "gold_plus10": grid[f"2200_{ret}_1"]["v"],
        "vol10": run.value(BASE_RETURN, volatility=0.10)[0],
        "vol20": run.value(BASE_RETURN, volatility=0.20)[0],
        "overrun_off": grid[f"{int(SPOT)}_{ret}_0"]["v"],
        "late2": run.value(BASE_RETURN, delay=2)[0],
    }

    prices = run.price_paths()
    quantiles = np.quantile(prices, [0.05, 0.5, 0.95], axis=0)
    gold_figures = {}
    for gold in GOLDS:
        # Price paths scale exactly with today's gold price under the same draws.
        end = prices[:, FAN_YEARS] * (gold / SPOT)
        p5, p50, p95 = np.quantile(end, [0.05, 0.5, 0.95])
        gold_figures[str(int(gold))] = {"p5": whole(p5), "median": whole(p50), "p95": whole(p95)}

    odds: dict[str, int | None] = {}
    value_m: dict[str, int] = {}
    for key, cell in grid.items():
        value_m[key] = whole(cell["v"])
        for price in PRICES:
            odds[f"{price}_{key}"] = implied_odds(price, cell["v"])

    def at_base(value: float) -> int | None:
        return implied_odds(BASE_PRICE, value)

    sensitivity = {
        "base": at_base(grid[base_key]["v"]),
        "rows": [
            {
                "name": "Gold price today",
                "from": "US$2,200",
                "to": "US$1,800",
                "a": at_base(tornado["gold_plus10"]),
                "b": at_base(tornado["gold_minus10"]),
            },
            {
                "name": "Extra return the buyer needs",
                "from": "8%",
                "to": "12%",
                "a": at_base(grid[f"{int(SPOT)}_8_1"]["v"]),
                "b": at_base(grid[f"{int(SPOT)}_12_1"]["v"]),
            },
            {
                "name": "Cost overruns",
                "from": "none",
                "to": "as in past mines",
                "a": at_base(tornado["overrun_off"]),
                "b": at_base(grid[base_key]["v"]),
            },
            {
                "name": "Built late",
                "from": "on time",
                "to": "2 years late",
                "a": at_base(grid[base_key]["v"]),
                "b": at_base(tornado["late2"]),
            },
            {
                "name": "How much gold swings",
                "from": "10% a year",
                "to": "20% a year",
                "a": at_base(tornado["vol10"]),
                "b": at_base(tornado["vol20"]),
            },
        ],
    }

    # Bridge steps are differences of the rounded running totals, so they add up.
    totals = [
        whole(bridge[k]) for k in ("study", "market_no_overrun", "market_overrun", "at_return")
    ]
    bridge_steps = {
        "study": totals[0],
        "market": totals[1] - totals[0],
        "overruns": totals[2] - totals[1],
        "return": totals[3] - totals[2],
        "worth_if_built": totals[3],
    }

    ratios = run.overrun_ratios()
    gates = run.gate_draws()

    return {
        "schema_version": SCHEMA_VERSION,
        "note": "Illustrative mine, made up to show the method. Engine output; not a forecast.",
        "meta": {
            "engine_version": importlib.metadata.version("pricedin"),
            "commit": _commit(),
            "n_paths": n_paths,
            "seed": seed,
        },
        "inputs": {
            "headline": {
                "initial_capex_usd_m": HEADLINE.initial_capex,
                "preproduction_years": HEADLINE.preproduction_years,
                "life_years": HEADLINE.life_years,
                "payable_koz_per_year": HEADLINE.payable_koz_per_year,
                "aisc_usd_per_oz": HEADLINE.aisc_per_oz,
                "gold_deck_usd_per_oz": HEADLINE.gold_deck,
                "tax_rate": HEADLINE.tax_rate,
                "study_discount_rate": HEADLINE.discount_rate,
                "npv_after_tax_usd_m": HEADLINE.npv_after_tax,
                "irr_after_tax": HEADLINE.irr_after_tax,
            },
            "gold_spot_usd_per_oz": SPOT,
            "real_rate": REAL_RATE,
            "gold_volatility": VOLATILITY,
            "years_to_start": TIMING.years_to_start,
            "max_wait_years": TIMING.max_wait,
            "overrun_prior": "capex.overrun.fs",
            "build_rule": True,
        },
        "controls": {
            "prices": list(PRICES),
            "golds": [int(g) for g in GOLDS],
            "returns": [round(r * 100) for r in EXTRA_RETURNS],
            "default": {
                "price": BASE_PRICE,
                "gold": int(SPOT),
                "return": round(BASE_RETURN * 100),
                "overrun": 1,
            },
        },
        "study_npv_check": round(run.study_check(), 1),
        "grid": {
            k: {"v": round(c["v"], 1), "se": round(c["se"], 2), "built": round(c["built"], 4)}
            for k, c in grid.items()
        },
        "value_m": value_m,
        "odds": odds,
        "se_max": round(max(cell["se"] for cell in grid.values()), 1),
        "tornado": {k: round(v, 1) for k, v in tornado.items()},
        "sensitivity": sensitivity,
        "bridge": {k: round(v, 1) for k, v in bridge.items()},
        "bridge_steps": bridge_steps,
        "cf": [round(float(x), 1) for x in calibration.after_tax],
        "paths": np.round(prices[:FAN_PATHS], 0).tolist(),
        "q": np.round(quantiles, 0).tolist(),
        "gold_figures": gold_figures,
        "gate_draws": [round(float(x), 4) for x in gates[:FAN_PATHS]],
        "npv": STUDY_NPV,
        "irr": HEADLINE.irr_after_tax,
        "overrun_hist": _hist(ratios),
        "overrun_summary": {
            "mean_pct": whole((float(ratios.mean()) - 1) * 100),
            "double_or_more_in_100": whole(float((ratios >= 2.0).mean()) * 100),
        },
    }


def main() -> None:
    """Write the export."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--paths", type=int, default=N_PATHS)
    args = parser.parse_args()
    data = export(args.paths)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {args.out} (study NPV check {data['study_npv_check']})")


if __name__ == "__main__":
    main()
