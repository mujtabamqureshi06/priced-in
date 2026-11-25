"""Phase 5, protocol section 8: the NAV multiple implied by the stage table.

A holder who values a project at its study NAV once construction is decided, and at
nothing before, pays today the study NAV times the expected discount factor to the
decision date, ``M = E[(1 + r)^-T ; T <= H]``, where ``T`` is the time from the study
to a construction decision by any owner and ``H`` the horizon. With ``r = 0`` this is
the cumulative incidence at ``H``. The multiple is derived from the stage table, not
observed in any price. It leaves out capital overrun, financing dilution, takeover
premia and any value an unbuilt project keeps after ``H``.

The multiple is estimated from the primary table (ADR 0068) with
``stage_table.discounted_incidence``. The engine check runs ``simulate`` on every gold
case in ``cases/`` at the study's own deck and rate with construction delayed ``k``
whole years, and reports the largest gap between ``V_k / V_0`` and ``(1 + r)^-k``. A
gap of zero means the engine and the closed form give the same multiple.

    uv run python scripts/phase5_implied_multiple.py OUTPUT_MD
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from pricedin.engine import Market, Risks, Timing, simulate
from pricedin.inputs import load_case
from pricedin.stage_table import discounted_incidence

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase5_stage_table import STAGES, Options, build, git_head

ROOT = Path(__file__).resolve().parents[1]
RATES = (0.0, 0.05, 0.08)
HORIZON_YEARS = (3, 5, 10)
DELAYS = range(11)


def delay_gap(case_path: Path) -> tuple[float, float]:
    """Study rate and the largest gap between V_k / V_0 and (1 + r)^-k."""
    case = load_case(case_path)
    market = Market.study_deck(case)
    values = [
        float(
            np.mean(
                simulate(
                    case, market, Timing(added_delay=k), Risks(), n_paths=10, seed=1
                ).project_value
            )
        )
        for k in DELAYS
    ]
    rate = market.discount_rate
    gap = max(abs(v / values[0] - (1.0 + rate) ** -k) for k, v in zip(DELAYS, values, strict=True))
    return rate, gap


def main() -> None:
    """Write the section 8 tables to the path given on the command line."""
    out_path = Path(sys.argv[1])
    a = build(Options(components=True)).arrays()
    cols = [(h, r) for h in HORIZON_YEARS for r in RATES]
    out = [
        "# Phase 5 section 8: implied NAV multiple (derived, not observed)",
        "",
        f"Commit {git_head()}, run {datetime.now(UTC).isoformat(timespec='seconds')}.",
        "",
        "Multiple of study NAV = expected discount factor to a construction decision "
        "within the horizon, primary table. r = 0 gives the cumulative incidence.",
        "",
        "| Stage | Entries | " + " | ".join(f"{h} y, r {r:.0%}" for h, r in cols) + " |",
        "|" + "---|" * (2 + len(cols)),
    ]
    for stage in STAGES:
        idx = a["stage"] == stage
        t, e = a["t_dec"][idx], a["ev_dec"][idx]
        cells = []
        for h, r in cols:
            m = discounted_incidence(t, e, r, 12.0 * h)
            cells.append("n/a" if np.isnan(m) else f"{m:.2f}x")
        out.append(f"| {stage} | {int(idx.sum())} | " + " | ".join(cells) + " |")
    out += [
        "",
        "Beyond about 4 years the curve rests increasingly on the earlier studies (later "
        "studies are censored), so the 10-year column describes 2012-2016 studies more "
        "than the frame as a whole.",
        "",
        "## Engine check: construction delayed k = 0 to 10 years at the study's deck",
        "",
        "| Case | Study rate | Largest gap, V_k/V_0 against (1+r)^-k |",
        "|---|---|---|",
    ]
    for path in sorted((ROOT / "cases").glob("*.yaml")):
        if path.name.startswith("_") or "commodity: gold" not in path.read_text("utf-8"):
            continue
        rate, gap = delay_gap(path)
        out.append(f"| {path.stem} | {rate:.1%} | {gap:.2e} |")
    out_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
