"""Priced In: a small app over the engine (#65).

Run locally with:  uv run --extra app streamlit run app/streamlit_app.py

Every number comes from the engine and the sourced inputs in this repository. The app
adds no assumptions of its own; the sliders change only inputs that the decision
records already treat as sensitivities.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import streamlit as st

from pricedin import defaults
from pricedin.engine import Market, Risks, RoyaltyClaim, fixed_nominal_advance, simulate
from pricedin.inputs import load_case
from pricedin.inversion import break_even_spread, royalty_frontier
from pricedin.priors import load_priors
from pricedin.report import project_waterfall
from pricedin.sensitivity import build_year_distribution, project_readout
from pricedin.snapshots import load_snapshot

ROOT = Path(__file__).resolve().parents[1]

CASES = {
    "South Railroad (Nevada; PFS 2020; valued June 7, 2021)": {
        "file": "south_railroad.yaml",
        "snapshot": "2021-06-07.yaml",
        "units": "US$ thousand",
        "royalty": True,
    },
    "Osino Twin Hills (Namibia; DFS 2023; valued July 13, 2023)": {
        "file": "osino_twin_hills.yaml",
        "snapshot": "2023-07-13.yaml",
        "units": "US$ million",
        "royalty": False,
    },
}

st.set_page_config(page_title="Priced In", layout="wide")
st.title("Priced In")
st.caption(
    "A simulation engine for undeveloped mining assets. It values the project, the "
    "operator's equity and a royalty on the same simulated futures, and shows a price as a "
    "share of the value if built, read as build odds and timing only at a stated required "
    "return. Results are illustrations under stated, "
    "sourced assumptions; they are not investment advice."
)

name = st.sidebar.selectbox("Case", list(CASES))
cfg = CASES[name]
n_paths = st.sidebar.select_slider("Simulated paths", [5_000, 20_000, 200_000], 200_000)
st.sidebar.caption(
    "200,000 paths with seed 1 reproduces the published figures. Fewer paths run faster "
    "and move the numbers within their standard errors."
)
y = st.sidebar.select_slider("Gold convenience yield", [0.0, 0.005, 0.01], 0.0)
st.sidebar.caption("Zero is the headline and is flagged; 1% is the sensitivity (ADR 0024).")


def _inputs(case_name: str, convenience_yield: float):  # type: ignore[no-untyped-def]
    """Case, priors, snapshot, market, risks and timing for one case."""
    c = CASES[case_name]
    case = load_case(ROOT / "cases" / str(c["file"]))
    priors = load_priors(ROOT / "data" / "priors.yaml")
    snap = load_snapshot(ROOT / "data" / "snapshots" / str(c["snapshot"]))
    market = Market.from_snapshot(snap, convenience_yield=float(convenience_yield))
    risks = Risks(
        stage_odds=defaults.stage_odds(priors, case.study.stage),
        overrun=defaults.overrun(priors, case.study.stage),
        build_rule=True,
    )
    timing = defaults.timing(priors, case.id)
    return case, priors, snap, market, risks, timing


@st.cache_data(show_spinner="Running the simulation...")
def _valuation(case_name: str, convenience_yield: float, paths: int):  # type: ignore[no-untyped-def]
    case, priors, _, market, risks, timing = _inputs(case_name, convenience_yield)
    steps = project_waterfall(case, market, timing, risks, n_paths=paths, seed=1)
    res = simulate(
        case,
        market,
        timing,
        risks,
        financing=defaults.equity_financing(priors),
        n_paths=paths,
        seed=1,
    )
    assert res.equity_value is not None
    return steps, res.estimate(res.equity_value)


@st.cache_data(show_spinner="Running the simulation...")
def _royalty(  # type: ignore[no-untyped-def]
    case_name: str, convenience_yield: float, paths: int, credited: bool, spread: float
):
    case, _, snap, market, risks, timing = _inputs(case_name, convenience_yield)
    r = snap.value("real_yield_10y")
    amr, infl = fixed_nominal_advance(
        120_000, snap.value("usdcad"), snap.value("cad_nominal_10y"), r, 1_000
    )
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
        n_paths=paths,
        seed=1,
    )
    be = break_even_spread(
        case,
        market,
        timing,
        replace(risks, overrun=None),
        claim,
        price,
        n_paths=paths,
        seed=1,
    )
    return frontier, be


@st.cache_data(show_spinner="Running the simulation...")
def _timing(case_name: str, convenience_yield: float, paths: int):  # type: ignore[no-untyped-def]
    case, _, _, market, risks, timing = _inputs(case_name, convenience_yield)
    return build_year_distribution(simulate(case, market, timing, risks, n_paths=paths, seed=1))


case, priors, snap, market, risks, timing = _inputs(name, float(y))
units = str(cfg["units"])

tabs = ["Valuation", "Timing", "Assumptions"]
if cfg["royalty"]:
    tabs.insert(1, "Royalty price")
views = dict(zip(tabs, st.tabs(tabs), strict=True))

with views["Valuation"]:
    steps, (eq, se) = _valuation(name, float(y), n_paths)
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
    st.metric(f"Equity claim, all-equity funding ({units})", f"{eq:,.1f}", help=f"s.e. {se:.1f}")

if "Royalty price" in views:
    with views["Royalty price"]:
        credited = st.toggle("Advances credited against later royalties", value=True)
        spread = st.slider("Buyer's real spread over the risk-free rate", 0.0, 0.20, 0.04, 0.002)
        frontier, be = _royalty(name, float(y), n_paths, credited, float(spread))
        st.write(
            "The price as a share of the value if built, for each number of years late, "
            "read as implied odds of construction at the spread chosen above (ADR 0025, "
            "ADR 0061). Values above one mean the price is above the certain-build value "
            "at that delay."
        )
        st.line_chart(
            {
                "years late": [p.added_delay for p in frontier.points],
                "implied odds": [min(p.gate_odds, 1.0) for p in frontier.points],
            },
            x="years late",
            y="implied odds",
        )
        st.write(
            f"Zero-delay odds: {frontier.zero_delay_odds:.2f}. Frontier shape: "
            f"{frontier.shape}. Break-even spread: "
            f"{'not in 0% to 50%' if be is None else f'{be:.1%}'}. "
            "Reference points as market-consistent spreads: Osisko's 2020 goodwill-test "
            "rate (3.5% post-tax, 4.76% pre-tax, on a flat deck) is equivalent to about "
            "3.5% to 4.7% for a royalty (ADR 0045); the Wharf control is about 15.8% "
            "(ADR 0028)."
        )

with views["Timing"]:
    shares = _timing(name, float(y), n_paths)
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
