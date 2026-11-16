"""Regenerate the South Railroad illustration (ADR 0028). Prints Markdown tables.

Usage: uv run python scripts/south_railroad_case.py
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from pricedin.controls import implied_spread, load_control
from pricedin.engine import Market, Overrun, Risks, RoyaltyClaim, Timing, fixed_nominal_advance
from pricedin.inputs import load_case
from pricedin.inversion import break_even_spread, royalty_frontier, zero_delay_odds_curve
from pricedin.priors import ShiftedLognormal, load_priors
from pricedin.snapshots import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
N, SEED = 20_000, 1
PRICE = 2079.0  # US$ thousands, ADR 0020
PRICE_CAPITALISED = 2317.0
OSISKO_POST_TAX, OSISKO_TAX = 0.035, 0.265  # Osisko 2020 audited statements, Notes 19, 26


def main() -> None:
    """Print the tables."""
    case = load_case(ROOT / "cases" / "south_railroad.yaml")
    priors = load_priors(ROOT / "data" / "priors.yaml")
    snap = load_snapshot(ROOT / "data" / "snapshots" / "2021-06-07.yaml")
    market = Market.from_snapshot(snap, convenience_yield=0.0)
    r = snap.value("real_yield_10y")
    dist = priors.get("capex.overrun.pfs").distribution
    assert isinstance(dist, ShiftedLognormal)
    risks = Risks(overrun=Overrun(dist, 0.914), build_rule=True)
    timing = Timing(years_to_start=4, max_wait=5)
    amr, infl = fixed_nominal_advance(
        120_000, snap.value("usdcad"), snap.value("cad_nominal_10y"), r, 1_000
    )
    claim = RoyaltyClaim(0.00633, 0.35, amr, True, 0.0, infl)

    wharf = load_control(ROOT / "controls" / "wharf.yaml")
    s_wharf = implied_spread(
        wharf.price.value,
        wharf.royalty_rate.value,
        wharf.payable_gold_oz,
        wharf.gold_spot.value,
        wharf.real_rate.value,
    )
    anchors = {
        "Osisko raw (post-tax 3.5%)": OSISKO_POST_TAX - r,
        "Osisko pre-tax equivalent (4.76%)": OSISKO_POST_TAX / (1 - OSISKO_TAX) - r,
        "Wharf control": s_wharf,
    }
    be = break_even_spread(case, market, timing, risks, claim, PRICE, n_paths=N, seed=SEED)
    be_cap = break_even_spread(
        case, market, timing, risks, claim, PRICE_CAPITALISED, n_paths=N, seed=SEED
    )
    print(f"Break-even spread (US$2.079M): {be:.4f}; (US$2.317M): {be_cap:.4f}")
    print("\n| Anchor | Real spread | Zero-delay odds |\n|---|---|---|")
    for name, s in anchors.items():
        q = zero_delay_odds_curve(
            case, market, timing, risks, claim, PRICE, (s,), n_paths=N, seed=SEED
        )[0][1]
        shown = f"{q:.2f}" if q <= 1 else "no solution (price above certain-build value)"
        print(f"| {name} | {s:.2%} | {shown} |")

    grid = tuple(x / 100 for x in range(0, 21, 2))
    print("\n| Real spread | Zero-delay odds, credited | Not credited |\n|---|---|---|")
    cred = zero_delay_odds_curve(
        case, market, timing, risks, claim, PRICE, grid, n_paths=N, seed=SEED
    )
    nocred = zero_delay_odds_curve(
        case,
        market,
        timing,
        risks,
        replace(claim, amr_credited=False),
        PRICE,
        grid,
        n_paths=N,
        seed=SEED,
    )
    for (s, q1), (_, q2) in zip(cred, nocred, strict=True):
        f = lambda q: f"{q:.2f}" if q <= 1 else "no solution"  # noqa: E731
        print(f"| {s:.0%} | {f(q1)} | {f(q2)} |")

    for label, c in (("credited", claim), ("not credited", replace(claim, amr_credited=False))):
        for name in ("Osisko raw (post-tax 3.5%)", "Osisko pre-tax equivalent (4.76%)"):
            fr = royalty_frontier(
                case,
                market,
                timing,
                risks,
                replace(c, spread=anchors[name]),
                PRICE,
                max_delay=10,
                n_paths=N,
                seed=SEED,
            )
            pts = ", ".join(
                f"{p.added_delay}: {p.gate_odds:.2f}" if p.solvable else f"{p.added_delay}: n/s"
                for p in fr.points
            )
            cbd = fr.certain_build_delay
            cbd_text = "none within 10 years" if cbd is None else f"{cbd:.1f} years"
            print(
                f"\nFrontier at {name}, advances {label}: shape {fr.shape}; "
                f"certain-build delay {cbd_text}"
                f"\n  delay: odds -> {pts}"
            )


if __name__ == "__main__":
    main()
