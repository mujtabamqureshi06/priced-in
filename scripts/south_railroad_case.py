"""Regenerate the South Railroad illustration (ADRs 0028, 0045). Prints Markdown tables.

Reference rates (Osisko) are read the way their source applied them: gold flat in
real terms at spot, discounted at the stated rate (ADR 0045). The spread curve and the
break-even spread are in market-consistent mode. The Wharf control is a
market-consistent spread already.

Usage: uv run python scripts/south_railroad_case.py
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from pricedin import defaults
from pricedin.controls import implied_spread, load_control
from pricedin.engine import Market, Risks, RoyaltyClaim, fixed_nominal_advance
from pricedin.inputs import load_case
from pricedin.inversion import break_even_spread, royalty_frontier, zero_delay_odds_curve
from pricedin.priors import load_priors
from pricedin.sensitivity import delay_text, delay_threshold
from pricedin.snapshots import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
N, SEED = 200_000, 1  # published tables (standard errors shown)
PRICE = 2079.0  # US$ thousands, ADR 0020
PRICE_CAPITALISED = 2317.0
# Osisko Gold Royalties, 2020 audited statements: goodwill test (fair value less costs of
# disposal) at a post-tax real rate of 3.5% with long-term gold at US$1,600; statutory
# tax rate 26.5%.
OSISKO_POST_TAX, OSISKO_TAX = 0.035, 0.265
OSISKO_DECK = 1600.0


def _odds(q: float) -> str:
    return f"{q:.2f}" if q <= 1 else "no solution"


def main() -> None:
    """Print the tables."""
    case = load_case(ROOT / "cases" / "south_railroad.yaml")
    priors = load_priors(ROOT / "data" / "priors.yaml")
    snap = load_snapshot(ROOT / "data" / "snapshots" / "2021-06-07.yaml")
    market = Market.from_snapshot(snap, convenience_yield=0.0)
    r = snap.value("real_yield_10y")
    risks = Risks(overrun=defaults.overrun(priors, case.study.stage), build_rule=True)
    timing = defaults.timing(priors, "south_railroad")
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
    spot = snap.value("gold_spot")
    references = {
        "Osisko post-tax 3.5%": OSISKO_POST_TAX,
        "Osisko pre-tax equivalent 4.76%": OSISKO_POST_TAX / (1 - OSISKO_TAX),
    }
    be = break_even_spread(case, market, timing, risks, claim, PRICE, n_paths=N, seed=SEED)
    be_cap = break_even_spread(
        case, market, timing, risks, claim, PRICE_CAPITALISED, n_paths=N, seed=SEED
    )
    print(f"Break-even spread (US$2.079M): {be:.4f}; (US$2.317M): {be_cap:.4f}")
    print("\n| Reference | Method | Rate | Zero-delay odds (std. error) |\n|---|---|---|---|")
    for name, k in references.items():
        for gold, label in ((OSISKO_DECK, "Osisko's deck"), (spot, "spot")):
            fr = royalty_frontier(
                case,
                Market.flat(gold, k),
                timing,
                risks,
                claim,
                PRICE,
                max_delay=0,
                n_paths=N,
                seed=SEED,
            )
            p = fr.points[0]
            shown = f"{p.gate_odds:.2f} ({p.gate_odds_se:.3f})" if p.solvable else "no solution"
            print(f"| {name} | gold flat at {label} US${gold:,.0f} | {k:.2%} | {shown} |")
    q = zero_delay_odds_curve(
        case, market, timing, risks, claim, PRICE, (s_wharf,), n_paths=N, seed=SEED
    )[0][1]
    print(f"| Wharf control | market-consistent spread | {s_wharf:.2%} | {_odds(q)} |")

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
        print(f"| {s:.0%} | {_odds(q1)} | {_odds(q2)} |")

    for label, c in (("credited", claim), ("not credited", replace(claim, amr_credited=False))):
        for name, k in references.items():
            fr = royalty_frontier(
                case,
                Market.flat(OSISKO_DECK, k),
                timing,
                risks,
                c,
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
                f"\nFrontier at {name} (gold flat at Osisko's deck), advances {label}: "
                f"shape {fr.shape}; certain-build delay {cbd_text}"
                f"\n  delay: odds -> {pts}"
            )

    d = delay_threshold(
        case,
        spot,
        r,
        snap.value("realised_vol_10y"),
        timing,
        risks,
        n_paths=50_000,
        seed=SEED,
    )
    print(f"\nProject value, every gate passed (ADR 0046). {delay_text(d)}")


if __name__ == "__main__":
    main()
