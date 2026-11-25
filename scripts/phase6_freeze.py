"""Phase 6 freeze (protocol 8.8 step 5): price ranges and benchmarks on frozen inputs.

Reads the price-free deal inputs, the market snapshots for each announcement date, the
study decks and the spread set, and writes for every deal its 80% range, central value,
the B1 and B2 benchmark values and its value-against-spread curve. No deal price is read.

    uv run python scripts/phase6_freeze.py INPUTS_DIR SNAPSHOT_DIR DECKS_CSV \
        FY_RATES_CSV OUT_DIR [--not-stated real|nominal]

The inputs and outputs hold per-deal values, which stay private (protocol section 6);
only this script and the hashes it prints are committed. Seeds are fixed: spreads and
Monte Carlo paths at ``SEED``; incidence replicates at the Phase 5 seed. Every deal uses
the same spread draws (common random numbers).
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import numpy as np

from pricedin import deal_pricer as dp
from pricedin.engine import Market
from pricedin.snapshots import load_snapshot
from pricedin.stage_table import months_between

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase5_stage_table import N_BOOT as P5_N_BOOT
from phase5_stage_table import SEED as P5_SEED
from phase5_stage_table import Options, build, git_head

ROOT = Path(__file__).resolve().parents[1]
SPREAD_SET = ROOT / "data" / "phase6" / "spread_set.csv"
N_DRAWS = 2_000
SEED = 20261126
#: CIM stage-based real rates for the B2 benchmark (protocol 8.7).
B2_RATES = {"PEA": 0.126, "PFS": 0.111, "FS": 0.089}
#: Spread grid for each deal's value-against-spread curve.
CURVE = (0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10, 0.15, 0.20)
#: Dates whose vendor gold close is stale; the LBMA PM is used instead (flagged).
STALE_VENDOR = {date(2023, 6, 8)}


def sha256(path: Path) -> str:
    """Hex SHA-256 of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stage_of(study_type: str) -> str:
    """Phase 5 stage for a study type (a DFS counts as FS)."""
    t = study_type.upper()
    if t in ("FS", "DFS", "BFS"):
        return "FS"
    if t in ("PEA", "PFS"):
        return t
    raise ValueError(f"unknown study type {study_type}")


def claim_from_input(d: dict[str, Any], inflation: float) -> dp.Claim:
    """Pricer terms from one transcribed input (``phase6_inputs`` schema)."""
    if d["instrument"] == "royalty":
        r = d["royalty"]
        adv = None
        if r.get("advance"):
            a = r["advance"]
            adv = dp.AdvanceMinimum(
                amount=float(a["amount"]),
                unit=a.get("unit", "money"),
                credited=bool(a.get("credited", True)),
                max_years=a.get("max_years"),
                max_total=a.get("max_total"),
            )
        steps = tuple(dp.RateStep(float(s["threshold"]), float(s["rate"])) for s in r["steps"])
        return dp.RoyaltyTerms(
            rate=float(r["rate"]),
            kind=r["kind"],
            coverage=float(d["covered_share"]),
            offsite_cost_per_oz=(
                float(d["offsite_cost_per_oz"])
                if d.get("offsite_cost_per_oz") is not None
                else None
            ),
            steps=steps,
            cap=float(r["cap"]) if r.get("cap") is not None else None,
            advance=adv,
            inflation=inflation if (r.get("cap") is not None or adv is not None) else 0.0,
            buyback=r.get("buyback", "none"),
            step_basis="covered" if not steps else r["step_basis"],
        )
    s = d["stream"]
    return dp.StreamTerms(
        share=float(s["share"]),
        payment=s["payment"],
        fixed_price=float(s.get("fixed_price") or 0.0),
        escalation=float(s.get("escalation") or 0.0),
        escalation_from=s.get("escalation_from") or "deal",
        inflation=inflation if s["payment"] != "share_of_spot" else 0.0,
        spot_share=float(s.get("spot_share") or 0.0),
        coverage=float(d["covered_share"]),
        steps=tuple(dp.DeliveryStep(float(x["threshold"]), float(x["share"])) for x in s["steps"]),
        step_basis=s["step_basis"],
        buyback=s.get("buyback", "none"),
    )


def stated_inflation(text: str) -> float | None:
    """Inflation stated with a rate ("2% (...)" gives 0.02); None when not stated."""
    m = re.match(r"\s*(-?\d+(?:\.\d+)?)\s*%", text)
    return float(m.group(1)) / 100.0 if m else None


def spread_rows(fy_rates: dict[str, tuple[float, float]], not_stated: str) -> list[dp.SpreadRow]:
    """Primary spread set (producing assets) converted to spreads (8.3 as amended).

    By deck shape, per row: a rate stated with an inflation assumption is applied to an
    escalating deck and is deflated at that rate; a flat deck needs no conversion,
    whatever the label; a deck not stated is treated as flat (``not_stated`` "real",
    the primary run, flagged) or deflated at the fiscal year-end breakeven ("nominal",
    the sensitivity). Then s = k(1 + r) at the fiscal year-end real rate.
    """
    rows = []
    with SPREAD_SET.open(encoding="utf-8") as f:
        for x in csv.DictReader(f):
            if x["asset_class"] != "producing":
                continue
            r, pi = fy_rates[x["fiscal_year"]]
            infl = stated_inflation(x["inflation_assumption_if_stated"])
            if infl is None and x["gold_price_deck_stated"].strip().lower() in ("", "not stated"):
                infl = pi if not_stated == "nominal" else None

            def to_spread(pct: str, r: float = r, infl: float | None = infl) -> float:
                k = float(pct) / 100.0
                if infl is not None:
                    k = dp.real_from_nominal(k, infl)
                return dp.spread_from_rate(k, r)

            lo, hi = to_spread(x["rate_low"]), to_spread(x["rate_high"])
            rows.append(dp.SpreadRow(x["company"], min(lo, hi), max(lo, hi)))
    return rows


@dataclass(frozen=True)
class DeckRow:
    """A study's own gold deck (US$/oz) and discount rate, for B1 and B2."""

    deck: float
    rate: float


def read_decks(path: Path) -> dict[str, DeckRow]:
    """Study decks keyed by deal; A$ decks are converted at the study's stated rate."""
    out = {}
    with path.open(encoding="utf-8") as f:
        for x in csv.DictReader(f):
            deck = float(x["deck_usd_per_oz"])
            if x["deck_currency"].strip().upper() in ("AUD", "A$") and x.get("fx_usd_per_unit"):
                deck *= float(x["fx_usd_per_unit"])
            out[x["deal_id"]] = DeckRow(deck, float(x["discount_rate"]) / 100.0)
    return out


def benchmark(
    claim: dp.Claim, schedule: list[float], deck: float, rate: float, pre: float | None
) -> float:
    """Study-convention value: flat deck, the given rate, decision at the deal date."""
    model = dp.cash_flow_model(claim, schedule, Market.flat(deck, rate), preproduction_years=pre)
    probs = dp.decision_timing(None, 0.0, already_decided=True).scenario_probs()
    return model.value(probs, 0.0)[0]


def main() -> None:
    """Price every deal marked ``priced`` and write the outputs and their hashes."""
    args = sys.argv[1:]
    not_stated = "real"
    if "--not-stated" in args:
        i = args.index("--not-stated")
        not_stated = args[i + 1]
        del args[i : i + 2]
    inputs, snaps, decks_csv, fy_csv, out_dir = (Path(a) for a in args)
    out_dir.mkdir(parents=True, exist_ok=True)

    with fy_csv.open(encoding="utf-8") as f:
        fy = {
            r["fiscal_year_end"][:4]: (float(r["dfii10_pct"]) / 100, float(r["t10yie_pct"]) / 100)
            for r in csv.DictReader(f)
        }
    rows = spread_rows(fy, not_stated)
    if not dp.meets_minimum(rows):
        raise SystemExit("spread set below the 8.3 minimum: illustrative grid only")
    spreads = dp.sample_spreads(rows, N_DRAWS, np.random.default_rng(SEED))
    decks = read_decks(decks_csv)
    a = build(Options(components=True)).arrays()

    results, curves = [], []
    for path in sorted(inputs.glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        if d["status"] != "priced":
            results.append({"deal_id": d["deal_id"], "status": d["status"]})
            continue
        announced = date.fromisoformat(d["announced"])
        snap = load_snapshot(snaps / f"{announced.isoformat()}.yaml")
        spot_key = "gold_lbma_pm" if announced in STALE_VENDOR else "gold_spot"
        market = dp.market_inputs(
            snap.value(spot_key), snap.value("real_yield_10y"), snap.value("realised_vol_10y")
        )
        claim = claim_from_input(d, snap.value("breakeven_10y"))
        model = dp.cash_flow_model(
            claim, d["schedule_oz"], market, preproduction_years=d["preproduction_years"], seed=SEED
        )
        stage = stage_of(d["study"]["type"])
        decided = d["construction_decision_before_announcement"] is not None
        age = months_between(date.fromisoformat(d["study"]["date"]), announced)
        idx = a["stage"] == stage
        t, e, cl = a["t_dec"][idx], a["ev_dec"][idx], list(a["cluster"][idx])
        reps = None
        if not decided:
            reps = dp.incidence_replicates(
                t, e, cl, n_boot=N_DRAWS, seed=P5_SEED, exclude_project=d["phase5_project_id"]
            )
        pr = dp.price_range(
            model, spreads, replicates=reps, age_months=age, already_decided=decided
        )
        central_inc = None if decided else dp.leave_project_out(t, e, cl, d["phase5_project_id"])
        timing = dp.decision_timing(central_inc, age, already_decided=decided)
        for s in CURVE:
            curves.append(
                {
                    "deal_id": d["deal_id"],
                    "spread": s,
                    "value": model.value(timing.scenario_probs(), s)[0],
                }
            )
        dk = decks[d["deal_id"]]
        b1 = benchmark(claim, d["schedule_oz"], dk.deck, dk.rate, d["preproduction_years"])
        b2 = benchmark(claim, d["schedule_oz"], dk.deck, B2_RATES[stage], d["preproduction_years"])
        results.append(
            {
                "deal_id": d["deal_id"],
                "status": "priced",
                "stage": stage,
                "age_months": round(age, 2),
                "already_decided": decided,
                "p10": pr.p10,
                "p50": pr.p50,
                "p90": pr.p90,
                "width_log": float(np.log(pr.p90 / pr.p10)),
                "max_relative_se": pr.max_relative_se,
                "needs_extension": pr.needs_extension,
                "b1": b1,
                "b2": b2,
                "spot_used": spot_key,
                "flags": "; ".join([*pr.flags, *d.get("flags", [])]),
            }
        )

    fields = sorted({k for r in results for k in r}, key=lambda k: (k != "deal_id", k))
    out_csv = out_dir / f"ranges_{not_stated}.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(results)
    curve_csv = out_dir / f"curves_{not_stated}.csv"
    with curve_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["deal_id", "spread", "value"])
        w.writeheader()
        w.writerows(curves)
    manifest = {
        "run_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "engine_commit": git_head(),
        "not_stated_reading": not_stated,
        "phase5_n_boot_table": P5_N_BOOT,
        "spread_set": sha256(SPREAD_SET),
        "phase5_labels": sha256(ROOT / "data" / "phase5" / "labels.csv"),
        "phase5_frame": sha256(ROOT / "data" / "phase5" / "frame_entries.csv"),
        "phase5_components": sha256(ROOT / "data" / "phase5" / "components.csv"),
        "inputs": {p.name: sha256(p) for p in sorted(inputs.glob("*.json"))},
        "snapshots": {p.name: sha256(p) for p in sorted(snaps.glob("*.yaml"))},
        "decks": sha256(decks_csv),
        "fy_rates": sha256(fy_csv),
        "ranges": sha256(out_csv),
        "curves": sha256(curve_csv),
    }
    (out_dir / f"manifest_{not_stated}.json").write_text(json.dumps(manifest, indent=1))
    print(json.dumps(manifest, indent=1))


if __name__ == "__main__":
    main()
