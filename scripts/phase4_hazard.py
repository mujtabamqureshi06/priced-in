"""Phase 4 secondary analysis: discrete-time hazard on quarterly snapshots (ADR 0060).

Inputs (paths given on the command line; the quarterly values are licensed-data derived
and kept private, the labels are public):

    uv run python scripts/phase4_hazard.py QUARTERLY_CSV ENTRY_ODDS_CSV [LABELS_CSV]

QUARTERLY_CSV has one row per project and quarter-end with columns project_id,
quarter_end, odds_0, odds_10 and status. ENTRY_ODDS_CSV is the frozen entry-snapshot
file; its rows with status "ok" and no exclusion define the primary panel. The script
writes the commit it runs from and the run time in UTC before any result.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from collections import defaultdict
from datetime import UTC, date, datetime
from pathlib import Path

import numpy as np
from scipy.optimize import minimize  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
FLOOR = 0.005
N_BOOT, SEED = 2_000, 20261120


def stage(text: str) -> str:
    """Map an entry-study label to PEA, PFS or FS (ADR 0060 rule 3)."""
    t = text.upper()
    if "PFS" in t or "PRE-FEAS" in t:
        return "PFS"
    if "FS" in t or "BFS" in t or "DFS" in t:
        return "FS"
    return "PEA"


def add_months(d: date, months: int) -> date:
    """Return the same day ``months`` later (day clipped to 28 where needed)."""
    y, m = divmod(d.month - 1 + months, 12)
    return date(d.year + y, m + 1, min(d.day, 28))


def design(rows: list[dict[str, object]], key: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Covariate matrix [1, log ratio, PFS, FS], outcomes and cluster ids."""
    x = np.array(
        [
            [
                1.0,
                np.log(max(float(r[key]), FLOOR)),  # type: ignore[arg-type]
                float(r["stage"] == "PFS"),
                float(r["stage"] == "FS"),
            ]
            for r in rows
        ]
    )
    y = np.array([float(r["y"]) for r in rows])  # type: ignore[arg-type]
    g = np.array([str(r["project_id"]) for r in rows])
    return x, y, g


def firth_cloglog(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Complementary log-log fit with a Firth (Jeffreys-prior) penalty."""

    def neg_pen_loglik(beta: np.ndarray) -> float:
        eta = np.clip(x @ beta, -30.0, 5.0)
        mu = np.clip(1.0 - np.exp(-np.exp(eta)), 1e-12, 1.0 - 1e-12)
        ll = float(np.sum(y * np.log(mu) + (1.0 - y) * np.log(1.0 - mu)))
        dmu = np.exp(eta - np.exp(eta))
        w = dmu**2 / (mu * (1.0 - mu))
        info = x.T @ (x * w[:, None])
        sign, logdet = np.linalg.slogdet(info)
        pen = 0.5 * logdet if sign > 0 else -1e6
        return -(ll + pen)

    start = np.zeros(x.shape[1])
    start[0] = np.log(-np.log(1.0 - max(y.mean(), 1e-3)))
    res = minimize(neg_pen_loglik, start, method="BFGS")
    return np.asarray(res.x)


def fit_with_ci(rows: list[dict[str, object]], key: str) -> tuple[float, float, float, int, int]:
    """Log-ratio coefficient, its cluster-bootstrap 95% interval, rows and events."""
    x, y, g = design(rows, key)
    beta = firth_cloglog(x, y)[1]
    ids = np.unique(g)
    index = {p: np.flatnonzero(g == p) for p in ids}
    rng = np.random.default_rng(SEED)
    draws = []
    for _ in range(N_BOOT):
        pick = rng.choice(ids, size=ids.size, replace=True)
        rows_b = np.concatenate([index[p] for p in pick])
        if y[rows_b].sum() == 0:
            continue
        draws.append(firth_cloglog(x[rows_b], y[rows_b])[1])
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return float(beta), float(lo), float(hi), int(y.size), int(y.sum())


def main() -> None:
    """Build the project-quarter table, fit the model and the stated checks."""
    quarterly_path, entry_path = sys.argv[1], sys.argv[2]
    labels_path = sys.argv[3] if len(sys.argv) > 3 else str(ROOT / "data/phase4/labels.csv")
    commit = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    ).stdout.strip()
    print(f"commit {commit}; run at {datetime.now(UTC).isoformat(timespec='seconds')}")

    def read(path: str) -> list[dict[str, str]]:
        with open(path, newline="") as fh:
            return list(csv.DictReader(fh))

    panel = {
        r["project_id"]
        for r in read(entry_path)
        if r.get("status") == "ok" and not r.get("excluded")
    }
    labels = {r["project_id"]: r for r in read(labels_path)}
    by_project: dict[str, list[dict[str, str]]] = defaultdict(list)
    dropped = 0
    for r in read(quarterly_path):
        if r["project_id"] not in panel:
            continue
        if r.get("status") != "ok" or r["odds_0"] in ("", "inf"):
            dropped += 1
            continue
        by_project[r["project_id"]].append(r)

    rows: list[dict[str, object]] = []
    for pid, quarters in by_project.items():
        lab = labels[pid]
        window_end = add_months(date.fromisoformat(lab["entry_study_date"]), 36)
        outcome = lab["outcome"]
        when = date.fromisoformat(lab["outcome_date"]) if lab["outcome_date"] else None
        stop = min(d for d in (window_end, when) if d is not None)
        quarters.sort(key=lambda q: q["quarter_end"])
        kept = [q for q in quarters if date.fromisoformat(q["quarter_end"]) < stop]
        for i, q in enumerate(kept):
            t = date.fromisoformat(q["quarter_end"])
            nxt = add_months(t, 3)
            event = outcome == "construction_decision" and when is not None and t < when <= nxt
            rows.append(
                {
                    "project_id": pid,
                    "quarter_end": t,
                    "odds_0": q["odds_0"],
                    "odds_10": q["odds_10"] if q["odds_10"] not in ("", "inf") else q["odds_0"],
                    "stage": stage(lab["entry_study"]),
                    "y": int(event),
                    "conf": lab["confidence"],
                    "before_end": len(kept) - i,
                    "outcome": outcome,
                    "floored": float(q["odds_0"]) < FLOOR,
                    "odds_0_lag2": kept[i - 2]["odds_0"] if i >= 2 else None,
                }
            )
    print(f"project-quarters {len(rows)}; projects {len(by_project)}; dropped unvalued {dropped}")

    def report(name: str, subset: list[dict[str, object]], key: str = "odds_0") -> None:
        b, lo, hi, n, ev = fit_with_ci(subset, key)
        print(
            f"{name:52s} rows {n:4d} events {ev:2d}  log-ratio coef {b:+.3f} "
            f"[{lo:+.3f}, {hi:+.3f}]  HR per doubling {2**b:.2f}"
        )

    report("Primary (ADR 0060)", rows)
    report(
        "(a) ratio from two quarter-ends earlier",
        [r for r in rows if r["odds_0_lag2"] is not None],
        "odds_0_lag2",
    )
    report("(b) without floored ratios", [r for r in rows if not r["floored"]])
    report(
        "(c) high- and medium-confidence labels",
        [r for r in rows if r["conf"] in ("high", "medium")],
    )
    report("(d) ratio at 10% spread", rows, "odds_10")
    report(
        "(e) without the two quarters before each change of control",
        [r for r in rows if not (r["outcome"] == "takeover" and r["before_end"] <= 2)],
    )


if __name__ == "__main__":
    main()
