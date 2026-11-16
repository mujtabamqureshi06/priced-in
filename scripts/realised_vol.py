"""Annualised realised gold volatility from a daily price CSV (date,price).

Usage: python scripts/realised_vol.py PRICES.csv AS_OF YEARS

Uses weekday log returns over the trailing YEARS years up to and including AS_OF and
annualises with sqrt(252). The price file is not stored in the repository; download it
from Alpha Vantage (GOLD_SILVER_HISTORY, symbol GOLD, interval daily).
"""

from __future__ import annotations

import csv
import itertools
import math
import sys
from datetime import date, timedelta


def realised_vol(rows: list[tuple[date, float]], as_of: date, years: int) -> float:
    """Annualised standard deviation of weekday log returns in the window."""
    start = as_of - timedelta(days=365 * years)
    window = sorted((d, p) for d, p in rows if start <= d <= as_of and d.weekday() < 5)
    returns = [math.log(b[1] / a[1]) for a, b in itertools.pairwise(window)]
    mean = sum(returns) / len(returns)
    var = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
    return math.sqrt(var * 252)


def main() -> None:
    """Read the CSV and print the volatility."""
    path, as_of, years = sys.argv[1], date.fromisoformat(sys.argv[2]), int(sys.argv[3])
    with open(path, encoding="utf-8") as f:
        rows = [(date.fromisoformat(r["date"]), float(r["price"])) for r in csv.DictReader(f)]
    print(f"{realised_vol(rows, as_of, years):.4f}")


if __name__ == "__main__":
    main()
