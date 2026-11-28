"""Study-entry tool: one study's headline figures in, value if built out (Phase 7).

The function here is the whole tool. The website runs it in the reader's browser
through Pyodide, and the tests run the same function under CPython, so no figure on
the page is computed anywhere else.

Settings are the ones the builder was validated on (``docs/phase7/builder_validation.md``):
the parametric schedule (``pricedin.parametric``), market-consistent gold at the given
spot, real rate and volatility, construction one year out with no waiting, the
price-dependent build rule, the stage's capital overrun prior and the equity financing
prior, 20,000 paths and seed 1. Scoping and PEA studies use the PFS overrun prior, as in
the validation.

The output is a plain dictionary of numbers and strings, so it crosses to JavaScript
unchanged.
"""

from __future__ import annotations

from dataclasses import fields, replace
from datetime import date
from typing import Any

from pricedin import defaults
from pricedin.engine import Market, Risks, Timing, simulate
from pricedin.parametric import Headline, build_case
from pricedin.priors import PriorsRegistry

N_PATHS = 20_000
SEED = 1
STAGES = ("PEA", "PFS", "FS")

#: Builder error on the 10 fresh tables (``docs/phase7/builder_validation.md``).
BUILDER_ERROR = {"median": 0.032, "p90": 0.107, "tables": 10}
#: Below this NPV-to-capital ratio the fresh test has no tables.
MARGINAL_NPV_TO_CAPEX = 0.5


def _headline(figures: dict[str, Any]) -> Headline:
    names = {f.name for f in fields(Headline)}
    unknown = sorted(set(figures) - names)
    if unknown:
        raise ValueError(f"unknown headline fields: {', '.join(unknown)}")
    return Headline(**figures)


def evaluate(
    figures: dict[str, Any],
    stage: str,
    market: dict[str, float],
    priors: PriorsRegistry,
    *,
    n_paths: int = N_PATHS,
    seed: int = SEED,
) -> dict[str, Any]:
    """Value one study's project if built, from its headline figures.

    Args:
        figures: the ``Headline`` fields (real US$ millions, thousand ounces, fractions).
        stage: ``PEA``, ``PFS`` or ``FS``.
        market: ``gold_spot`` (real US$/oz), ``real_rate`` and ``volatility`` (annual).
        priors: the priors registry (``data/priors.yaml``).
        n_paths: simulated gold paths.
        seed: random seed.

    Returns:
        ``value_if_built`` and its Monte Carlo ``standard_error`` (US$ millions),
        ``share_built``, the calibration ``basis``, the validated builder error and a
        list of ``notes`` on where the validation gives no evidence.

    Raises:
        ValueError: if the figures are inconsistent, the stage is unknown or the
            builder cannot match the study's NPV and IRR.

    """
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {', '.join(STAGES)}, got {stage!r}")
    for key in ("gold_spot", "real_rate", "volatility"):
        if key not in market:
            raise ValueError(f"market needs {key}")
    h = _headline(figures)
    case = build_case(
        h,
        case_id="entry",
        name="Study entered by the reader",
        operator="not stated",
        jurisdiction="not stated",
        as_of=date(2000, 1, 1),
        stage=stage,
        document_title="Headline figures entered by the reader",
        document_url="https://example.org/entered",
        document_date=date(2000, 1, 1),
        location="entered figures",
    )
    overrun_stage = "PFS" if stage == "PEA" else stage
    risks = Risks(stage_odds=1.0, overrun=defaults.overrun(priors, overrun_stage), build_rule=True)
    m = replace(
        Market.market_consistent(
            float(market["gold_spot"]), float(market["real_rate"]), 0.0, float(market["volatility"])
        ),
        discount_rate=float(market["real_rate"]),
    )
    r = simulate(
        case,
        m,
        Timing(years_to_start=1, max_wait=0),
        risks,
        financing=defaults.equity_financing(priors),
        n_paths=n_paths,
        seed=seed,
    )
    value, se = r.estimate(r.project_value)
    npv, _ = h.target()
    notes = []
    if npv / h.initial_capex < MARGINAL_NPV_TO_CAPEX:
        notes.append(
            "NPV is below half of initial capital; the fresh validation tables include no "
            "such project, and in-sample errors were largest there."
        )
    return {
        "value_if_built": float(value),
        "standard_error": float(se),
        "share_built": float(r.built.mean()),
        "basis": h.basis,
        "stage": stage,
        "n_paths": n_paths,
        "seed": seed,
        "builder_error": dict(BUILDER_ERROR),
        "notes": notes,
    }
