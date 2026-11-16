"""Replicate the Brennan and Schwartz (1985) copper mine by least-squares Monte Carlo.

Prints the published finite-difference values beside this package's estimates, for
every copper price in the benchmark file (ADR 0040). About 80 seconds per price.

Usage: uv run python scripts/brennan_schwartz.py
"""

from __future__ import annotations

from pathlib import Path

import yaml

from pricedin.switching import SwitchingMine, value_switching_mine

ROOT = Path(__file__).resolve().parents[1]
N_PATHS, SEED = 40_000, 1


def main() -> None:
    """Print the comparison table."""
    bench = yaml.safe_load(
        (ROOT / "data" / "benchmarks" / "brennan_schwartz_1985.yaml").read_text(encoding="utf-8")
    )
    mine = SwitchingMine(**bench["parameters"])
    print(
        "| Copper price (US$/lb) | Open: published | Open: LSM (std. error) "
        "| Closed: published | Closed: LSM (std. error) |"
    )
    print("|---|---|---|---|---|")
    for price, (open_ref, closed_ref) in bench["values"].items():
        res = value_switching_mine(mine, float(price), n_paths=N_PATHS, seed=SEED)
        print(
            f"| {float(price):.2f} | {open_ref:.2f} | {res.open_value:.2f} ({res.open_se:.2f}) "
            f"| {closed_ref:.2f} | {res.closed_value:.2f} ({res.closed_se:.2f}) |",
            flush=True,
        )


if __name__ == "__main__":
    main()
