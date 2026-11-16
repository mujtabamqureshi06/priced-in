"""Priced In: a small app over the engine (WP 1.12).

Run locally with:  uv run --extra app streamlit run app/streamlit_app.py

Every number comes from the engine and the sourced inputs in this repository. The app
adds no assumptions of its own; the sliders change only inputs that the decision
records already treat as sensitivities.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import streamlit as st

from pricedin.engine import (
    Financing,
    Market,
    Overrun,
    Risks,
    RoyaltyClaim,
    Timing,
    fixed_nominal_advance,
    simulate,
)
from pricedin.inputs import load_case
from pricedin.inversion import break_even_spread, royalty_frontier
from pricedin.priors import ShiftedLognormal, load_priors
from pricedin.report import project_waterfall
from pricedin.sensitivity import build_year_distribution, project_readout
from pricedin.snapshots import load_snapshot

ROOT = Path(__file__).resolve().parents[1]

CASES = {
    "South Railroad (Nevada; PFS 2020; valued June 7, 2021)": {
        "file": "south_railroad.yaml",
        "snapshot": "2021-06-07.yaml",
        "overrun": "capex.overrun.pfs",
        "stage_odds": 0.82 * 0.88,
        "years_to_start": 4,
        "units": "US$ thousand",
        "royalty": True,
    },
    "Osino Twin Hills (Namibia; DFS 2023; valued July 13, 2023)": {
        "file": "osino_twin_hills.yaml",
        "snapshot": "2023-07-13.yaml",
        "overrun": "capex.overrun.fs",
        "stage_odds": 0.88,
        "years_to_start": 1,
        "units": "US$ million",
        "royalty": False,
    },
}

st.set_page_config(page_title="Priced In", layout="wide")
st.title("Priced In")
st.caption(
    "A simulation engine for undeveloped mining assets. It values the project, the "
    "operator's equity and a royalty on the same simulated futures, and shows what a "
    "price implies about build odds and timing. Results are illustrations under stated, "
    "sourced assumptions; they are not investment advice."
)

name = st.sidebar.selectbox("Case", list(CASES))
cfg = CASES[name]
n_paths = st.sidebar.select_slider("Simulated paths", [2_000, 5_000, 10_000, 20_000], 5_000)
y = st.sidebar.select_slider("Gold convenience yield", [0.0, 0.005, 0.01], 0.0)
st.sidebar.caption("Zero is the headline and is flagged; 1% is the sensitivity (ADR 0024).")

case = load_case(ROOT / "cases" / str(cfg["file"]))
priors = load_priors(ROOT / "data" / "priors.yaml")
snap = load_snapshot(ROOT / "data" / "snapshots" / str(cfg["snapshot"]))
market = Market.from_snapshot(snap, convenience_yield=float(y))
dist = priors.get(str(cfg["overrun"])).distribution
assert isinstance(dist, ShiftedLognormal)
risks = Risks(stage_odds=float(cfg["stage_odds"]), overrun=Overrun(dist, 0.914), build_rule=True)
timing = Timing(years_to_start=int(cfg["years_to_start"]), max_wait=5)
units = str(cfg["units"])

tabs = ["Valuation", "Timing", "Assumptions"]
if cfg["royalty"]:
    tabs.insert(1, "Royalty price")
views = dict(zip(tabs, st.tabs(tabs), strict=True))

with views["Valuation"]:
    steps = project_waterfall(case, market, timing, risks, n_paths=n_paths, seed=1)
    st.write(project_readout(case.name, units, steps))
    st.table(
        {
            "Step": [s.label + (f" ({s.note})" if s.note else "") for s in steps],
            f"Value ({units})": [f"{s.value:,.1f}" for s in steps],
            "Change": [f"{s.change:+,.1f}" for s in steps],
            "Std. error": [f"{s.standard_error:.1f}" for s in steps],
        }
    )
    st.bar_chart({s.label: s.change for s in steps[1:]})
    res = simulate(
        case, market, timing, risks, financing=Financing(0.0, 0.1054), n_paths=n_paths, seed=1
    )
    assert res.equity_value is not None
    eq, se = res.estimate(res.equity_value)
    st.metric(f"Equity claim, all-equity funding ({units})", f"{eq:,.1f}", help=f"s.e. {se:.1f}")

if "Royalty price" in views:
    with views["Royalty price"]:
        r = snap.value("real_yield_10y")
        amr, infl = fixed_nominal_advance(
            120_000, snap.value("usdcad"), snap.value("cad_nominal_10y"), r, 1_000
        )
        credited = st.toggle("Advances credited against later royalties", value=True)
        spread = st.slider("Buyer's real spread over the risk-free rate", 0.0, 0.20, 0.0558, 0.002)
        claim = RoyaltyClaim(0.00633, 0.35, amr, credited, spread, infl)
        price = 2079.0
        frontier = royalty_frontier(
            case,
            market,
            timing,
            replace(risks, overrun=None),
            claim,
            price,
            max_delay=10,
            n_paths=n_paths,
            seed=1,
        )
        st.write(
            "Implied odds of construction for each number of years late, for a project "
            "that is built (ADR 0025). Values above one mean the price is above the "
            "certain-build value at that delay."
        )
        st.line_chart(
            {
                "years late": [p.added_delay for p in frontier.points],
                "implied odds": [min(p.gate_odds, 1.0) for p in frontier.points],
            },
            x="years late",
            y="implied odds",
        )
        be = break_even_spread(
            case,
            market,
            timing,
            replace(risks, overrun=None),
            claim,
            price,
            n_paths=n_paths,
            seed=1,
        )
        st.write(
            f"Zero-delay odds: {frontier.zero_delay_odds:.2f}. Frontier shape: "
            f"{frontier.shape}. Break-even spread: "
            f"{'not in 0% to 50%' if be is None else f'{be:.1%}'}. "
            "Reference points: Osisko impairment rate about 4.3% to 5.6%; Wharf control "
            "about 15.8% (ADR 0028)."
        )

with views["Timing"]:
    res = simulate(case, market, timing, risks, n_paths=n_paths, seed=1)
    shares = build_year_distribution(res)
    st.bar_chart(shares)
    st.caption(
        "Years after the valuation date. 'Never built' covers stage failure and paths "
        "the build rule never builds within its window (ADR 0023)."
    )

with views["Assumptions"]:

    def describe(d: object) -> str:
        """Distribution parameters as text."""
        fields = {k: v for k, v in vars(d).items() if k != "kind"}
        return ", ".join(
            f"{k} {v:g}" if isinstance(v, float) else f"{k} {v}" for k, v in fields.items()
        )

    rows = [
        {
            "id": p.id,
            "value": describe(p.distribution),
            "units": p.units,
            "status": str(p.status),
            "source": p.source,
            "flag": p.flag,
        }
        for p in priors.priors.values()
    ]
    st.dataframe(rows, width="stretch")
    st.caption(
        "Status: V verified, V-abs abstract only, S secondary, P practitioner, "
        "J stated judgment. Every decision is an ADR in docs/decisions/."
    )
