"""What the price-to-value ratio measures at a 0% spread (methodology section 7).

For each gold case at spot equal to the study price, 15% volatility and construction one
year out, with the overrun prior, the build rule and the default equity financing:

- the equity value if built, at a 1% and a 0% real rate, as a multiple of the study's
  undiscounted after-tax cash flow (operator share);
- the change in project value when the real rate moves from 0% to 1%.

Usage: uv run python scripts/ratio_diagnostics.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from pricedin import defaults
from pricedin.engine import Market, Risks, Timing, simulate
from pricedin.inputs import load_case
from pricedin.inversion import equity_frontier
from pricedin.priors import load_priors

ROOT = Path(__file__).resolve().parents[1]
N, SEED = 50_000, 1
CASES = [("osino_twin_hills", "FS"), ("south_railroad", "PFS"), ("south_railroad_fs2022", "FS")]


def main() -> None:
    """Print the multiples and the real-rate effect for each case."""
    priors = load_priors(ROOT / "data" / "priors.yaml")
    financing = defaults.equity_financing(priors)
    timing = Timing(years_to_start=1)
    for case_id, stage in CASES:
        case = load_case(ROOT / "cases" / f"{case_id}.yaml")
        deck = case.study.price_deck["gold"].value
        flows = np.asarray(case.schedule.columns["cash_flow_after_tax"].values, dtype=np.float64)
        undiscounted = float(flows.sum()) * case.operator_share
        risks = Risks(overrun=defaults.overrun(priors, stage), build_rule=True)
        row = []
        for rate in (0.0, 0.01):
            market = Market.market_consistent(deck, rate, 0.0, 0.15)
            frontier = equity_frontier(
                case, market, timing, risks, financing, 1.0, max_delay=0, n_paths=N, seed=SEED
            )
            project = simulate(case, market, timing, risks, n_paths=N, seed=SEED).project_value
            row.append((frontier.points[0].value_if_passed, float(project.mean())))
        (v0, p0), (v1, p1) = row
        print(
            f"{case_id}: equity if built / undiscounted after-tax cash flow "
            f"{v1 / undiscounted:.2f} at 1%, {v0 / undiscounted:.2f} at 0%; "
            f"project value, real rate 0% to 1%: {p1 / p0 - 1:+.1%}"
        )


if __name__ == "__main__":
    main()
