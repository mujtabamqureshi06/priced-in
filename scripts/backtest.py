"""Regenerate every number in docs/backtest.md (WP 2.8) with one command.

Runs, in order: the Wharf control, the South Railroad royalty illustration (ADR 0028),
the Osino prices (ADRs 0031 to 0033) and the Sorby Hills royalty (ADR 0035), then the
transaction dataset summary. Each section prints the Markdown tables that the write-up
and the case notes quote.

Usage: uv run python scripts/backtest.py
"""

from __future__ import annotations

import runpy
from pathlib import Path

from pricedin.controls import implied_spread, load_control
from pricedin.transactions import load_transactions

ROOT = Path(__file__).resolve().parents[1]
CASE_SCRIPTS = ("south_railroad_case.py", "osino_prices.py", "sorby_hills_case.py")


def main() -> None:
    """Print each section in turn."""
    wharf = load_control(ROOT / "controls" / "wharf.yaml")
    s = implied_spread(
        wharf.price.value,
        wharf.royalty_rate.value,
        wharf.payable_gold_oz,
        wharf.gold_spot.value,
        wharf.real_rate.value,
    )
    print(f"## Wharf control\n\nImplied real spread: {s:.2%}\n")
    for name in CASE_SCRIPTS:
        print(f"## {name}\n")
        runpy.run_path(str(ROOT / "scripts" / name), run_name="__main__")
        print()
    print("## Transaction dataset\n")
    print("| Deal | Scope | Note |")
    print("|---|---|---|")
    for deal in load_transactions(ROOT / "data" / "transactions.csv"):
        print(f"| {deal.deal_id} | {deal.scope.value} | {deal.scope_note} |")


if __name__ == "__main__":
    main()
