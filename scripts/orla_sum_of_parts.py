"""What Orla Mining's market value implies for South Railroad, by sum of parts (#75).

Valuation date: August 12, 2022, the day Orla closed its acquisition of Gold Standard
Ventures (ADR 0044). Inputs are in `data/sum_of_parts/orla_2022-08-12.yaml`.

    South Railroad price = enterprise value + PV of corporate G&A
                           - Camino Rojo (producing) - Cerro Quema (range)

Exploration ground is valued at zero, so the residual is an upper bound for South
Railroad. Camino Rojo and South Railroad are valued at the same real spread; the
residual band comes from Cerro Quema, entered from zero to its study NPV. Each end of
the band is read as implied odds against the South Railroad project claim (Orla funds
construction, ADR 0031) on the 2022 feasibility study.

Usage: uv run python scripts/orla_sum_of_parts.py
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from pricedin import defaults
from pricedin.engine import Market, Risks
from pricedin.inputs import load_case
from pricedin.inversion import project_frontier
from pricedin.priors import load_priors
from pricedin.snapshots import load_snapshot
from pricedin.sum_of_parts import (
    Part,
    ProducingAsset,
    producing_value,
    residual_band,
    treasury_shares,
)

ROOT = Path(__file__).resolve().parents[1]
N, SEED = 200_000, 1  # published tables (standard errors shown)


def load() -> dict[str, Any]:
    """Load the sum-of-parts input file."""
    path = ROOT / "data" / "sum_of_parts" / "orla_2022-08-12.yaml"
    data: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data


def enterprise_value(d: dict[str, Any], fx: float) -> tuple[float, float, float]:
    """Return (equity value, net debt, enterprise value) in US$ million."""
    eq = d["equity"]
    price = eq["share_price_usd"]["value"]
    instruments = [(eq["options"]["count_millions"], eq["options"]["strike_cad"] / fx)]
    instruments += [(w["count_millions"], w["strike_cad"] / fx) for w in eq["warrants"]]
    basic = eq["basic_shares_millions"]["value"] + eq["share_units_millions"]["value"]
    shares, proceeds = treasury_shares(basic, instruments, price)
    equity = price * shares - proceeds
    nd = d["net_debt"]
    debt = nd["credit_facility"]["value"] + nd["fresnillo_obligation"]["value"]
    net_debt = (debt + nd["leases"]["value"] - nd["cash"]["value"]) / 1000.0
    net_debt -= nd["gsv_cash_less_leases_cad"]["value"] / fx / 1000.0
    return equity, net_debt, equity + net_debt


def camino_rojo(d: dict[str, Any]) -> ProducingAsset:
    """Camino Rojo's remaining study cash flows (US$ million)."""
    cr = d["camino_rojo"]
    n = len(cr["periods"])
    times = np.array([cr["y1_time"]] + [cr["y2_time"] + k for k in range(n - 1)])
    scale = np.ones(n)
    scale[0] = cr["y1_fraction"]
    return ProducingAsset(
        times=times,
        gold_revenue=np.asarray(cr["gold_revenue"]["values"]) * scale / 1000.0,
        after_tax=np.asarray(cr["after_tax"]["values"]) * scale / 1000.0,
        deck=cr["deck"]["gold"],
        linked_share=cr["linked_share"]["value"],
        tax_rate=cr["tax_rate"]["value"],
    )


def cerro_quema_high(d: dict[str, Any], spot: float) -> float:
    """Cerro Quema's study NPV at the spot gold price, interpolated (US$ million)."""
    table = d["cerro_quema"]["after_tax_npv5_by_gold_price"]
    prices = sorted(float(k) for k in table)
    return float(np.interp(spot, prices, [table[int(p)] for p in prices]))


def main() -> None:
    """Print the tables."""
    d = load()
    snap = load_snapshot(ROOT / "data" / "snapshots" / "2022-08-12.yaml")
    fx, spot, r = snap.value("usdcad"), snap.value("gold_spot"), snap.value("real_yield_10y")
    base = Market.market_consistent(spot, r, 0.0, snap.value("realised_vol_10y"))
    priors = load_priors(ROOT / "data" / "priors.yaml")
    timing = defaults.timing(priors, "south_railroad_fs2022")
    years = timing.years_to_start
    case = load_case(ROOT / "cases" / "south_railroad_fs2022.yaml")
    risks = Risks(overrun=defaults.overrun(priors, case.study.stage), build_rule=True)

    equity, net_debt, ev = enterprise_value(d, fx)
    ga = d["corporate_ga"]["per_year"]["value"] / 1000.0
    horizon = years + len(case.schedule.periods)
    ga_pv = ga * float(((1 + r) ** -np.arange(1, horizon + 1)).sum())
    cq_high = cerro_quema_high(d, spot)
    cr = camino_rojo(d)
    print(
        f"Equity US${equity:,.1f}M, net debt US${net_debt:,.1f}M, enterprise value "
        f"US${ev:,.1f}M; PV of corporate G&A over {horizon} years US${ga_pv:,.1f}M; "
        f"Cerro Quema 0 to US${cq_high:,.1f}M; gold US${spot:,.2f}, US$1 = C${fx:.4f}"
    )
    print(
        "\n| Real spread | Camino Rojo | South Railroad price | Value if built on schedule "
        "| Implied odds |\n|---|---|---|---|---|"
    )
    for spread in (0.0, 0.04, 0.08, 0.12, 0.15):
        m = replace(base, discount_rate=r + spread)
        cr_value = producing_value(cr, spot, base.drift, r + spread)
        band = residual_band(
            ev,
            [
                Part("Camino Rojo", cr_value, cr_value),
                Part("Cerro Quema", 0.0, cq_high),
                Part("Corporate G&A", -ga_pv, -ga_pv),
            ],
        )
        f = project_frontier(case, m, timing, risks, 1.0, max_delay=0, n_paths=N, seed=SEED)
        v_pass = f.points[0].value_if_passed / 1000.0
        lo, hi = band.low / v_pass, band.high / v_pass
        if lo > 1:
            odds = "above 1"
        else:
            odds = f"{lo:.2f} to {hi:.2f}" if hi <= 1 else f"{lo:.2f} to above 1"
        print(
            f"| {spread:.0%} | {cr_value:,.1f} | {band.low:,.1f} to {band.high:,.1f} | "
            f"{v_pass:,.1f} | {odds} |"
        )


if __name__ == "__main__":
    main()
