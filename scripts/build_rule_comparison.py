"""Compare the fixed build rule with the least-squares Monte Carlo rule (ADR 0038).

1. Osino Twin Hills on the December 15, 2023 snapshot: project value and mean build
   year under each rule, across the gold convenience yield and a project-level spread.
2. South Railroad on the June 7, 2021 snapshot: zero-delay implied odds of the Vox price
   at the Osisko reference spreads, and the build timing, under each rule.

Usage: uv run python scripts/build_rule_comparison.py
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from pricedin import defaults
from pricedin.engine import (
    Market,
    Risks,
    RoyaltyClaim,
    fixed_nominal_advance,
    simulate,
)
from pricedin.inputs import load_case
from pricedin.inversion import royalty_frontier
from pricedin.priors import load_priors
from pricedin.snapshots import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
PRIORS = load_priors(ROOT / "data" / "priors.yaml")
N, SEED = 200_000, 1
SR_PATHS, SR_PRICE = 200_000, 2079.0  # US$ thousands (ADR 0020)
OSISKO_POST_TAX, OSISKO_TAX = 0.035, 0.265  # Osisko 2020 audited statements (ADR 0028)


def osino() -> None:
    """Print the Osino table."""
    case = load_case(ROOT / "cases" / "osino_twin_hills.yaml")
    snap = load_snapshot(ROOT / "data" / "snapshots" / "2023-12-15.yaml")
    timing = defaults.timing(PRIORS, "osino_twin_hills")
    print(
        "| Convenience yield | Project spread | Fixed rule: value (US$M), mean build year "
        "| LSM rule: value (US$M), mean build year |"
    )
    print("|---|---|---|---|")
    for y in (0.0, 0.01):
        for spread in (0.0, 0.05, 0.10, 0.15):
            base = Market.from_snapshot(snap, convenience_yield=y)
            market = replace(base, discount_rate=base.discount_rate + spread)
            cells = []
            for rule in ("fixed", "lsm"):
                risks = Risks(build_rule=True, build_decision=rule)
                res = simulate(case, market, timing, risks, n_paths=N, seed=SEED)
                value, se = res.estimate(res.project_value)
                year = float(res.build_year[res.built].mean())
                cells.append(f"{value:,.0f} (SE {se:,.0f}), {year:.1f}")
            print(f"| {y:.0%} | {spread:.1%} | {cells[0]} | {cells[1]} |")


def south_railroad() -> None:
    """Print the South Railroad comparison."""
    case = load_case(ROOT / "cases" / "south_railroad.yaml")
    snap = load_snapshot(ROOT / "data" / "snapshots" / "2021-06-07.yaml")
    market = Market.from_snapshot(snap, convenience_yield=0.0)
    r = snap.value("real_yield_10y")
    timing = defaults.timing(PRIORS, "south_railroad")
    amr, infl = fixed_nominal_advance(
        120_000, snap.value("usdcad"), snap.value("cad_nominal_10y"), r, 1_000
    )
    # Market-consistent spreads equivalent, for revenue, to the Osisko rates on a flat
    # deck: s = k(1 + r) (ADR 0045). Approximate here because of the advance royalties.
    spreads = {
        "Osisko 3.5%": OSISKO_POST_TAX * (1 + r),
        "pre-tax 4.76%": OSISKO_POST_TAX / (1 - OSISKO_TAX) * (1 + r),
    }
    print(
        "| Rule | Odds, spread equivalent to Osisko 3.5% | Odds, equivalent to 4.76% "
        "| Passing paths built | Mean build year |"
    )
    print("|---|---|---|---|---|")
    overrun = defaults.overrun(PRIORS, case.study.stage)
    rules = {
        "fixed (study 5%)": Risks(overrun=overrun, build_rule=True),
        "LSM (valuation rate)": Risks(overrun=overrun, build_rule=True, build_decision="lsm"),
        "LSM (study 5%)": Risks(
            overrun=overrun,
            build_rule=True,
            build_decision="lsm",
            lsm_rate=case.study.discount_rate.value,
        ),
    }
    for rule, risks in rules.items():
        odds = []
        for s in spreads.values():
            claim = RoyaltyClaim(0.00633, 0.35, amr, True, s, infl)
            f = royalty_frontier(
                case,
                market,
                timing,
                risks,
                claim,
                SR_PRICE,
                max_delay=0,
                n_paths=SR_PATHS,
                seed=SEED,
            )
            p = f.points[0]
            odds.append(f"{p.gate_odds:.3f} (SE {p.gate_odds_se:.3f})")
        claim = RoyaltyClaim(0.00633, 0.35, amr, True, spreads["Osisko 3.5%"], infl)
        res = simulate(case, market, timing, risks, royalty=claim, n_paths=SR_PATHS, seed=SEED)
        share = float(res.built[res.passed_gates].mean())
        year = float(res.build_year[res.built].mean())
        print(f"| {rule} | {odds[0]} | {odds[1]} | {share:.2f} | {year:.2f} |")


def main() -> None:
    """Print both tables."""
    osino()
    print()
    south_railroad()


if __name__ == "__main__":
    main()
