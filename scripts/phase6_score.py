"""Phase 6 scoring (protocol 8.8 step 6, sections 8.5 to 8.7) on the frozen ranges.

Joins the private price file to the frozen ranges and curves and writes the aggregate
results. Per-deal rows are written to the private output folder only; the printed
summary holds aggregates. Run only after the Phase 5 table is final.

    uv run python scripts/phase6_score.py RANGES_CSV CURVES_CSV PRICES_CSV OUT_DIR

Interval score (Gneiting and Raftery 2007) on log prices at alpha = 0.2:
``IS = (u - l) + (2 / alpha) (l - y) 1{y < l} + (2 / alpha) (y - u) 1{y > u}``.
B1-W and B2-W centre each benchmark value in a range of the engine's own log width.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import beta  # type: ignore[import-untyped]

ALPHA = 0.2
N_BOOT, SEED = 10_000, 20261127


def interval_score(lower: float, upper: float, y: float, alpha: float = ALPHA) -> float:
    """Interval score on logs of a positive range and outcome."""
    lo, hi, v = np.log(lower), np.log(upper), np.log(y)
    return float((hi - lo) + (2 / alpha) * max(lo - v, 0.0) + (2 / alpha) * max(v - hi, 0.0))


def centred(value: float, width: float) -> tuple[float, float]:
    """Return a range of log width ``width`` centred (in logs) on ``value``."""
    return value * np.exp(-width / 2), value * np.exp(width / 2)


def clopper_pearson(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Exact binomial interval for k successes in n."""
    a = (1 - level) / 2
    lo = 0.0 if k == 0 else float(beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a, k + 1, n - k))
    return lo, hi


def implied_spread(spreads: list[float], values: list[float], price: float) -> float | None:
    """Spread at which the central curve equals the price (log-linear interpolation).

    None when the price lies outside the curve's range of values.
    """
    s, v = np.asarray(spreads), np.log(np.asarray(values))
    p = np.log(price)
    if not (v.min() <= p <= v.max()):
        return None
    order = np.argsort(v)
    return float(np.interp(p, v[order], s[order]))


def main() -> None:
    """Score and write per-deal rows (private) and the aggregate summary."""
    ranges_csv, curves_csv, prices_csv, out_dir = (Path(a) for a in sys.argv[1:5])
    out_dir.mkdir(parents=True, exist_ok=True)
    with ranges_csv.open(encoding="utf-8") as f:
        ranges = {r["deal_id"]: r for r in csv.DictReader(f) if r["status"] == "priced"}
    with prices_csv.open(encoding="utf-8") as f:
        prices = {r["deal_id"]: float(r["price_usd"]) for r in csv.DictReader(f)}
    curves: dict[str, tuple[list[float], list[float]]] = {}
    with curves_csv.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            s, v = curves.setdefault(r["deal_id"], ([], []))
            s.append(float(r["spread"]))
            v.append(float(r["value"]))
    missing = sorted(set(ranges) - set(prices))
    if missing:
        raise SystemExit(f"no price for {missing}")

    rows = []
    for d, r in sorted(ranges.items()):
        y = prices[d]
        lo, mid, hi = float(r["p10"]), float(r["p50"]), float(r["p90"])
        w = float(r["width_log"])
        b1, b2 = float(r["b1"]), float(r["b2"])
        rows.append(
            {
                "deal_id": d,
                "stage": r["stage"],
                "inside": lo <= y <= hi,
                "side": "below" if y < lo else ("above" if y > hi else "inside"),
                "width": w,
                "ale_engine": abs(np.log(y / mid)),
                "ale_b1": abs(np.log(y / b1)),
                "ale_b2": abs(np.log(y / b2)),
                "is_engine": interval_score(lo, hi, y),
                "is_b1w": interval_score(*centred(b1, w), y),
                "is_b2w": interval_score(*centred(b2, w), y),
                "implied_spread": implied_spread(*curves[d], y),
            }
        )

    n = len(rows)
    k = sum(r["inside"] for r in rows)
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(N_BOOT, n))

    def boot(diff: np.ndarray) -> list[float]:
        means = diff[idx].mean(axis=1)
        return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]

    ise = np.array([r["is_engine"] for r in rows])
    d1 = ise - np.array([r["is_b1w"] for r in rows])
    d2 = ise - np.array([r["is_b2w"] for r in rows])
    widths = np.array([r["width"] for r in rows])
    imp = [r["implied_spread"] for r in rows if r["implied_spread"] is not None]
    summary = {
        "n_priced": n,
        "coverage_k": k,
        "coverage_interval_95": clopper_pearson(k, n),
        "misses_below": sum(r["side"] == "below" for r in rows),
        "misses_above": sum(r["side"] == "above" for r in rows),
        "width_median": float(np.median(widths)),
        "width_iqr": [float(np.percentile(widths, 25)), float(np.percentile(widths, 75))],
        "male_engine": float(np.median([r["ale_engine"] for r in rows])),
        "male_b1": float(np.median([r["ale_b1"] for r in rows])),
        "male_b2": float(np.median([r["ale_b2"] for r in rows])),
        "mean_is_engine": float(ise.mean()),
        "mean_is_b1w": float(np.mean([r["is_b1w"] for r in rows])),
        "mean_is_b2w": float(np.mean([r["is_b2w"] for r in rows])),
        "mean_diff_engine_minus_b1w": float(d1.mean()),
        "mean_diff_engine_minus_b1w_boot95": boot(d1),
        "mean_diff_engine_minus_b2w": float(d2.mean()),
        "mean_diff_engine_minus_b2w_boot95": boot(d2),
        "implied_spread_n": len(imp),
        "implied_spread_quartiles": (
            [float(np.percentile(imp, q)) for q in (25, 50, 75)] if imp else None
        ),
        "implied_spread_outside_curve": n - len(imp),
    }
    with (out_dir / "per_deal_scores.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
