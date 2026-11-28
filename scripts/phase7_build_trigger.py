"""Phase 7 build-trigger study (exploratory; `docs/phase7/build_trigger_spec.md`).

For each Phase 4 primary-panel project, the trigger G* is the lowest real gold price at
which the engine's threshold build rule says "build now" on the project's entry study.
The study asks whether a construction decision in the next quarter is associated with
real gold at a quarter-end standing above or below the project's trigger, conditional on
stage, on the Phase 4 quarterly panel (ADR 0060 rule 1).

    uv run python scripts/phase7_build_trigger.py HEADLINES_CSV MARKET_CSV [--synthetic]

HEADLINES_CSV has one row per project: project_id, the ``Headline`` fields, and
study_month (YYYY-MM, the money of the study's figures). MARKET_CSV has one row per
calendar quarter-end: quarter_end, gold_spot (US$/oz), real_rate, volatility and cpi
(CPIAUCSL for the quarter-end month), plus one row per study month with cpi only. Both
are private (the headline sets are transcriptions; the market file is rebuilt from
public series) and their SHA-256 hashes are printed first. The script refuses to fit
unless the rebuilt panel reconciles to 80 projects, 838 project-quarters and 16
decisions. ``--synthetic`` skips that check and is used by the tests only.
"""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from dataclasses import dataclass, fields
from datetime import UTC, date, datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase4_hazard import add_months, firth_cloglog, stage

from pricedin import defaults
from pricedin.engine import (
    Market,
    Risks,
    _decision_npv,
    _decision_value,
    _gate_costs,
)
from pricedin.parametric import Headline, _schedule, build_case, calibrate, irr_tolerance
from pricedin.priors import PriorsRegistry, load_priors

ROOT = Path(__file__).resolve().parents[1]
LABELS = ROOT / "data" / "phase4" / "labels.csv"
PHASE5_LABELS = ROOT / "data" / "phase5" / "labels.csv"
#: ADR 0058 rule 12: the 85 entries less Laiva and four without market data.
EXCLUDED = {"laiva", "enchi", "imperial", "kobada_primary", "mt_ida_and_bottle_creek"}
EXPECTED = (80, 838, 16)
N_BOOT, SEED = 2_000, 20261128
G_LO, G_HI = 100.0, 10_000.0
COST_SHIFT = 0.189  # in-sample 90th-percentile builder error (docs/phase7/builder_validation.md)
MIN_PROJECTS, MIN_EVENTS = 60, 12


def quarter_end_on_or_after(d: date) -> date:
    """Return the first calendar quarter-end on or after ``d``."""
    for m, last in ((3, 31), (6, 30), (9, 30), (12, 31)):
        e = date(d.year, m, last)
        if e >= d:
            return e
    raise AssertionError


def next_quarter_end(e: date) -> date:
    """Return the calendar quarter-end after ``e``."""
    y, m = (e.year, e.month + 3) if e.month < 12 else (e.year + 1, 3)
    return date(y, m, 31 if m in (3, 12) else 30)


def panel_quarters(labels: list[dict[str, str]]) -> list[dict[str, object]]:
    """Project-quarters by ADR 0060 rule 1, with the next-quarter outcome (rule 2)."""
    rows: list[dict[str, object]] = []
    for r in labels:
        entry = date.fromisoformat(r["entry_study_date"])
        when = (
            date.fromisoformat(r["outcome_date"])
            if r["outcome_date"] and r["outcome"] != "non_event"
            else None
        )
        stop = min(d for d in (add_months(entry, 36), when) if d is not None)
        t = quarter_end_on_or_after(entry)
        while t < stop:
            y = r["outcome"] == "construction_decision" and when is not None
            y = y and t < when <= add_months(t, 3)  # type: ignore[operator]
            rows.append(
                {
                    "project_id": r["project_id"],
                    "quarter_end": t,
                    "y": int(y),
                    "stage": stage(r["entry_study"]),
                    "entry_quarter": quarter_end_on_or_after(entry),
                }
            )
            t = next_quarter_end(t)
    return rows


@dataclass(frozen=True)
class MarketRow:
    """Market inputs at the entry snapshot."""

    gold_spot: float
    real_rate: float
    volatility: float


def trigger(
    h: Headline,
    stage_label: str,
    m: MarketRow,
    priors: PriorsRegistry,
    cost_scale: float = 1.0,
    irr_decimals: int | None = None,
) -> float | None:
    """Lowest real gold price at which the threshold build rule builds now, or None.

    The rule (``pricedin.engine.simulate`` with ``build_rule``): decision NPV at the
    study rate at or above the hurdle (0), and decision value net of the expected
    overrun and dilution at or above zero, at the entry snapshot's real rate and
    volatility. ``cost_scale`` multiplies the built operating cost (the sensitivity).
    Returns None when no price in [100, 10,000] US$/oz satisfies the rule.

    The schedule follows the Phase 4 calibration rules (ADR 0057 rules 1 and 2): the IRR
    tolerance is half a unit of the last digit the study states (``irr_decimals``), and
    an entry whose cash-flow shape cannot be matched keeps the closest schedule that
    matches its NPV. ``ValueError`` is raised only if the NPV cannot be matched.
    """
    irr_tol = irr_tolerance(irr_decimals) if irr_decimals is not None else 5e-4
    case = build_case(
        h,
        case_id="bt",
        name="bt",
        operator="bt",
        jurisdiction="bt",
        as_of=date(2000, 1, 1),
        stage="PFS" if stage_label == "PEA" else stage_label,
        document_title="bt",
        document_url="https://example.org/bt",
        document_date=date(2000, 1, 1),
        location="bt",
        irr_tol=irr_tol,
        allow_shape_miss=True,
    )
    if cost_scale != 1.0:
        base = calibrate(h, irr_tol=irr_tol, allow_shape_miss=True)
        shifted = _schedule(h, base.cost_factor * cost_scale, base.tilt)
        cols = dict(case.schedule.columns)
        for name, values in (
            ("payable_gold_koz", shifted.payable_koz),
            ("gold_revenue", shifted.gold_revenue),
            ("taxes", shifted.taxes),
            ("initial_capex", shifted.initial_capex),
            ("cash_flow_pre_tax", shifted.pre_tax),
            ("cash_flow_after_tax", shifted.after_tax),
        ):
            cols[name] = cols[name].model_copy(update={"values": [float(v) for v in values]})
        schedule = case.schedule.model_copy(update={"columns": cols})
        case = case.model_copy(update={"schedule": schedule})
    risks = Risks(
        stage_odds=1.0,
        overrun=defaults.overrun(priors, "PFS" if stage_label == "PEA" else stage_label),
        build_rule=True,
    )
    fin = defaults.equity_financing(priors)
    rate = case.study.discount_rate.value

    def ok(p: float) -> bool:
        mk = Market.market_consistent(p, m.real_rate, 0.0, m.volatility)
        gate = _gate_costs(case, mk, risks, fin)
        price = np.array([p])
        return bool(
            _decision_npv(case, price, rate)[0] >= risks.build_hurdle
            and _decision_value(case, mk, price, mk.discount_rate, gate)[0] >= 0.0
        )

    if not ok(G_HI):
        return None
    if ok(G_LO):
        return G_LO
    lo, hi = G_LO, G_HI
    while hi - lo > 0.01:
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if ok(mid) else (mid, hi)
    return hi


def fit(x: np.ndarray, y: np.ndarray, g: np.ndarray) -> tuple[float, float, float]:
    """Coefficient on the first non-intercept column and its cluster-bootstrap 95% CI."""
    beta = float(firth_cloglog(x, y)[1])
    ids = np.unique(g)
    index = {p: np.flatnonzero(g == p) for p in ids}
    rng = np.random.default_rng(SEED)
    draws = []
    for _ in range(N_BOOT):
        rows = np.concatenate([index[p] for p in rng.choice(ids, size=ids.size, replace=True)])
        if y[rows].sum() == 0:
            continue
        draws.append(firth_cloglog(x[rows], y[rows])[1])
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return beta, float(lo), float(hi)


def design(rows: list[dict[str, object]], key: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Columns [1, covariate, PFS, FS], outcomes and project ids."""
    x = np.array(
        [[1.0, float(r[key]), float(r["stage"] == "PFS"), float(r["stage"] == "FS")] for r in rows]  # type: ignore[arg-type]
    )
    y = np.array([float(r["y"]) for r in rows])  # type: ignore[arg-type]
    g = np.array([str(r["project_id"]) for r in rows])
    return x, y, g


def sha256(path: str) -> str:
    """Return the SHA-256 of a file."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path: str | Path) -> list[dict[str, str]]:
    """Read a CSV file as dictionaries."""
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def run(
    headlines_path: str, market_path: str, labels: list[dict[str, str]], *, synthetic: bool
) -> dict[str, object]:
    """Compute G*, build the covariates and fit the stated models. Returns the results."""
    priors = load_priors(ROOT / "data" / "priors.yaml")
    rows = panel_quarters(labels)
    n_proj = len({r["project_id"] for r in rows})
    counts = (n_proj, len(rows), sum(int(r["y"]) for r in rows))  # type: ignore[call-overload]
    print(f"panel: projects {counts[0]}, project-quarters {counts[1]}, decisions {counts[2]}")
    if not synthetic and counts != EXPECTED:
        raise SystemExit(f"panel does not reconcile to {EXPECTED}; stopping before any G*")

    heads = {r["project_id"]: r for r in read(headlines_path)}
    mkt = {r["quarter_end"]: r for r in read(market_path) if r.get("quarter_end")}
    cpi = {r["quarter_end"][:7]: float(r["cpi"]) for r in read(market_path) if r.get("cpi")}
    names = {f.name for f in fields(Headline)}
    stage_of = {str(r["project_id"]): str(r["stage"]) for r in rows}

    results: dict[str, object] = {"counts": counts}
    for label, scale in (
        ("primary", 1.0),
        ("cost -18.9%", 1 - COST_SHIFT),
        ("cost +18.9%", 1 + COST_SHIFT),
    ):
        g_star: dict[str, float] = {}
        missing = []
        shape_miss: set[str] = set()
        for pid in sorted(stage_of):
            if pid not in heads:
                missing.append(pid)
                continue
            raw = heads[pid]
            vals = {k: raw[k] for k in names if raw.get(k) not in (None, "")}
            h = Headline(
                **{
                    k: (int(float(v)) if k in ("preproduction_years", "life_years") else float(v))
                    for k, v in vals.items()
                }
            )
            entry_q = next(str(r["entry_quarter"]) for r in rows if r["project_id"] == pid)
            e = mkt[entry_q]
            dec = int(raw["irr_decimals"]) if raw.get("irr_decimals") not in (None, "") else None
            tol = irr_tolerance(dec) if dec is not None else 5e-4
            try:
                g = trigger(
                    h,
                    stage_of[pid],
                    MarketRow(float(e["gold_spot"]), float(e["real_rate"]), float(e["volatility"])),
                    priors,
                    scale,
                    dec,
                )
                if not calibrate(h, irr_tol=tol, allow_shape_miss=True).shape_matched:
                    shape_miss.add(pid)
            except ValueError:
                g = None
            if g is None:
                missing.append(pid)
            else:
                g_star[pid] = g
        kept = []
        for r in rows:
            pid = str(r["project_id"])
            if pid not in g_star:
                continue
            q = str(r["quarter_end"])
            real_spot = float(mkt[q]["gold_spot"]) * cpi[heads[pid]["study_month"]] / cpi[q[:7]]
            kept.append(
                {
                    **r,
                    "x": np.log(real_spot / g_star[pid]),
                    "above": float(real_spot >= g_star[pid]),
                }
            )
        n_k = len({r["project_id"] for r in kept})
        ev = sum(int(r["y"]) for r in kept)  # type: ignore[call-overload]
        print(
            f"{label}: projects with G* {n_k}, dropped {len(missing)},"
            f" rows {len(kept)}, decisions {ev}"
        )
        above_ev = sum(int(r["y"]) for r in kept if r["above"])  # type: ignore[call-overload]
        above_n = sum(1 for r in kept if r["above"])
        print(
            f"  descriptive: quarters above G* {above_n} with {above_ev} decisions;"
            f" below {len(kept) - above_n} with {ev - above_ev}"
        )
        out: dict[str, object] = {
            "projects": n_k,
            "rows": len(kept),
            "decisions": ev,
            "g_star": g_star,
        }
        if n_k < MIN_PROJECTS or ev < MIN_EVENTS:
            print("  stop rule: fewer than 60 projects or 12 decisions; descriptive only")
        else:
            b, lo, hi = fit(*design(kept, "x"))
            print(
                f"  log(real spot / G*) coef {b:+.3f} [{lo:+.3f}, {hi:+.3f}]"
                f"  HR per doubling {2**b:.2f}"
            )
            out["coef"] = (b, lo, hi)
            if label == "primary":
                print(f"  shape not matched (ADR 0057 rule 2): {len(shape_miss)} projects")
                sub = [r for r in kept if r["project_id"] not in shape_miss]
                b3, lo3, hi3 = fit(*design(sub, "x"))
                print(
                    f"  check, without shape-not-matched entries: coef {b3:+.3f}"
                    f" [{lo3:+.3f}, {hi3:+.3f}]"
                )
                out["no_shape_miss"] = (b3, lo3, hi3)
                b2, lo2, hi2 = fit(*design(kept, "above"))
                print(f"  secondary, spot >= G* coef {b2:+.3f} [{lo2:+.3f}, {hi2:+.3f}]")
                out["above"] = (b2, lo2, hi2)
        results[label] = out
    return results


def phase5_relabel(labels: list[dict[str, str]]) -> list[dict[str, str]]:
    """Sensitivity: Phase 5 construction labels for projects whose id matches."""
    p5 = {r["project_id"]: r for r in read(PHASE5_LABELS)}
    out, matched = [], 0
    for r in labels:
        q = p5.get(r["project_id"])
        if q is None:
            out.append(r)
            continue
        matched += 1
        r = dict(r)
        if q["outcome"] == "construction_decision" and q["decision_date"]:
            r["outcome"], r["outcome_date"] = "construction_decision", q["decision_date"]
        elif r["outcome"] == "construction_decision":
            r["outcome"], r["outcome_date"] = "non_event", ""
        out.append(r)
    print(f"Phase 5 labels matched for {matched} of {len(labels)} projects")
    return out


def main() -> None:
    """Run the primary analysis and the Phase 5 labels sensitivity."""
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    synthetic = "--synthetic" in sys.argv
    commit = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    ).stdout.strip()
    print(f"commit {commit}; run at {datetime.now(UTC).isoformat(timespec='seconds')}")
    print(f"headlines sha256 {sha256(args[0])}; market sha256 {sha256(args[1])}")
    labels = [
        r
        for r in read(LABELS)
        if r["panel"] in ("primary", "both") and r["project_id"] not in EXCLUDED
    ]
    run(args[0], args[1], labels, synthetic=synthetic)
    print("Sensitivity: Phase 5 labels (labels only)")
    run(args[0], args[1], phase5_relabel(labels), synthetic=True)


if __name__ == "__main__":
    main()
