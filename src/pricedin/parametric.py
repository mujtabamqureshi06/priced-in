"""Parametric study builder: an annual schedule from a study's headline figures (ADR 0051).

Phase 4 needs a mine plan at every snapshot of every project in the panel, and most
studies cannot be hand-transcribed at that scale. This module builds an annual
cash-flow schedule from the figures nearly every study reports, and calibrates it so
that it reproduces the study's own NPV and IRR exactly: after-tax figures where the study
reports them, otherwise its pre-tax figures, with tax then modelled from a regime written
down in advance (ADR 0054).

The schedule:

- initial capital spread evenly over ``preproduction_years`` periods, the first at t0;
- ``life_years`` production periods with payable gold ``Q_t = Q * (1 + g * z_t)``, where
  ``z_t`` runs linearly from -1 to 1 over the mine life, so ``g`` tilts production toward
  the early (``g < 0``) or late (``g > 0``) years and the life-of-mine total is unchanged;
- operating cost ``k * AISC * Q_t``, with all-in sustaining cost per ounce from the study;
- tax at the study's marginal rate on revenue less operating cost less straight-line
  depreciation of initial capital over the mine life, floored at zero.

Two unknowns, the cost factor ``k`` and the tilt ``g``, are solved so that the schedule's
after-tax NPV at the study rate and its after-tax IRR equal the study's. ``k`` absorbs
what the headline figures leave out (closure, working capital, royalties, other taxes);
``g`` stands in for grade and ramp-up profile. How well this approximates a transcribed
table is measured on a hand-transcribed validation subsample, not assumed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import brentq, least_squares  # type: ignore[import-untyped]

from pricedin.inputs import Case

FloatArray = NDArray[np.float64]

#: Production may not fall below this share of the average in any year.
MIN_PRODUCTION_SHARE = 0.05


@dataclass(frozen=True)
class Headline:
    """Headline figures from one study, in real US$ millions and thousand ounces.

    Attributes:
        initial_capex: initial capital, US$ millions.
        preproduction_years: whole years of construction before first production (>= 1).
        life_years: years of production.
        payable_koz_per_year: average payable gold per year, thousand ounces.
        aisc_per_oz: all-in sustaining cost, US$ per ounce.
        gold_deck: the study's gold price, US$ per ounce.
        tax_rate: marginal income-tax rate: the study's own where it reports after-tax
            figures, otherwise the modelled regime's combined rate.
        discount_rate: the study's real discount rate.
        npv_after_tax: after-tax NPV at ``discount_rate``, US$ millions, if reported.
        irr_after_tax: after-tax IRR, if reported.
        npv_pre_tax: pre-tax NPV at ``discount_rate``, US$ millions, if reported.
        irr_pre_tax: pre-tax IRR, if reported.

    At least one complete pair (NPV and IRR on the same basis) is required. When both
    are given, the schedule is calibrated to the after-tax pair.

    """

    initial_capex: float
    preproduction_years: int
    life_years: int
    payable_koz_per_year: float
    aisc_per_oz: float
    gold_deck: float
    tax_rate: float
    discount_rate: float
    npv_after_tax: float | None = None
    irr_after_tax: float | None = None
    npv_pre_tax: float | None = None
    irr_pre_tax: float | None = None

    @property
    def basis(self) -> str:
        """The basis the schedule is calibrated to: ``after-tax`` or ``pre-tax``."""
        if self.npv_after_tax is not None and self.irr_after_tax is not None:
            return "after-tax"
        return "pre-tax"

    def target(self) -> tuple[float, float]:
        """Return the (NPV, IRR) pair the schedule is calibrated to."""
        if self.basis == "after-tax":
            assert self.npv_after_tax is not None and self.irr_after_tax is not None
            return self.npv_after_tax, self.irr_after_tax
        assert self.npv_pre_tax is not None and self.irr_pre_tax is not None
        return self.npv_pre_tax, self.irr_pre_tax

    def __post_init__(self) -> None:
        """Reject inputs no schedule could match."""
        if self.preproduction_years < 1 or self.life_years < 2:
            raise ValueError("need at least one pre-production year and two production years")
        for name in ("initial_capex", "payable_koz_per_year", "aisc_per_oz", "gold_deck"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive")
        if not 0.0 <= self.tax_rate < 1.0:
            raise ValueError("tax_rate must be in [0, 1)")
        after = self.npv_after_tax is not None and self.irr_after_tax is not None
        pre = self.npv_pre_tax is not None and self.irr_pre_tax is not None
        if not (after or pre):
            raise ValueError("need an NPV and IRR on the same basis (after-tax or pre-tax)")
        npv, irr = self.target()
        if irr <= self.discount_rate and npv > 0:
            raise ValueError("a positive NPV needs an IRR above the discount rate")


@dataclass(frozen=True)
class Schedule:
    """A built schedule and the calibrated parameters."""

    payable_koz: FloatArray
    gold_revenue: FloatArray
    operating_cost: FloatArray
    initial_capex: FloatArray
    taxes: FloatArray
    pre_tax: FloatArray
    after_tax: FloatArray
    cost_factor: float
    tilt: float


def _schedule(h: Headline, k: float, g: float) -> Schedule:
    p, life = h.preproduction_years, h.life_years
    n = p + life
    z = np.linspace(-1.0, 1.0, life)
    koz = np.zeros(n)
    koz[p:] = h.payable_koz_per_year * (1.0 + g * z)
    revenue = koz * h.gold_deck / 1000.0
    cost = k * koz * h.aisc_per_oz / 1000.0
    capex = np.zeros(n)
    capex[:p] = h.initial_capex / p
    depreciation = np.zeros(n)
    depreciation[p:] = h.initial_capex / life
    taxes = h.tax_rate * np.maximum(revenue - cost - depreciation, 0.0)
    pre_tax = revenue - cost - capex
    return Schedule(koz, revenue, cost, capex, taxes, pre_tax, pre_tax - taxes, k, g)


def _npv(flows: FloatArray, rate: float) -> float:
    return float(flows @ (1.0 + rate) ** -np.arange(flows.size))


def _irr(flows: FloatArray) -> float:
    return float(brentq(lambda r: _npv(flows, r), -0.9, 10.0))


def calibrate(h: Headline) -> Schedule:
    """Solve the cost factor and tilt so the schedule reproduces the study NPV and IRR.

    The fit is to the after-tax pair when the study reports it, otherwise to the pre-tax
    pair; in the second case the schedule's after-tax flows are modelled with ``tax_rate``.

    Raises:
        ValueError: if no schedule within the bounds matches both figures to within
            0.1% of initial capital (NPV) and 0.05 points (IRR).

    """
    g_max = 1.0 - MIN_PRODUCTION_SHARE

    target_npv, target_irr = h.target()
    pre = h.basis == "pre-tax"

    def residual(x: FloatArray) -> FloatArray:
        s = _schedule(h, x[0], x[1])
        flows = s.pre_tax if pre else s.after_tax
        npv_err = (_npv(flows, h.discount_rate) - target_npv) / h.initial_capex
        try:
            irr_err = _irr(flows) - target_irr
        except ValueError:
            irr_err = 1.0
        return np.array([npv_err, irr_err])

    fit = least_squares(residual, x0=np.array([1.0, 0.0]), bounds=([0.0, -g_max], [5.0, g_max]))
    npv_err, irr_err = residual(fit.x)
    if abs(npv_err) > 1e-3 or abs(irr_err) > 5e-4:
        raise ValueError(
            "no schedule matches the study's NPV and IRR within tolerance "
            f"(NPV error {npv_err:.2%} of capex, IRR error {irr_err:.2%}); "
            "check the headline figures"
        )
    return _schedule(h, float(fit.x[0]), float(fit.x[1]))


def build_case(
    h: Headline,
    *,
    case_id: str,
    name: str,
    operator: str,
    jurisdiction: str,
    as_of: date,
    stage: str,
    document_title: str,
    document_url: str,
    document_date: date,
    location: str,
) -> Case:
    """Build a schedule-mode case from headline figures, for the engine and the inversion.

    Every column cites ``location`` in the named document, marked as built by this
    module, so a reader can tell a built schedule from a transcribed one.
    """
    s = calibrate(h)
    n = s.after_tax.size
    src = {"document": case_id, "location": f"{location}; schedule built by pricedin.parametric"}

    def col(values: FloatArray) -> dict[str, object]:
        return {"values": [round(float(v), 6) for v in values], "source": src}

    def qty(value: float, units: str) -> dict[str, object]:
        return {"value": value, "units": units, "source": src}

    raw = {
        "id": case_id,
        "name": name,
        "operator": operator,
        "jurisdiction": jurisdiction,
        "commodity": "gold",
        "currency": "USD",
        "as_of": as_of,
        "operator_share": 1.0,
        "documents": [
            {
                "id": case_id,
                "title": document_title,
                "issuer": operator,
                "date": document_date,
                "url": document_url,
            }
        ],
        "study": {
            "stage": stage,
            "document": case_id,
            "effective_date": document_date,
            "price_deck": {"gold": qty(h.gold_deck, "US$/oz")},
            "discount_rate": qty(h.discount_rate, "fraction per year"),
            "npv_pre_tax": qty(_npv(s.pre_tax, h.discount_rate), "US$ millions"),
            "npv_after_tax": qty(_npv(s.after_tax, h.discount_rate), "US$ millions"),
            "irr_after_tax": qty(_irr(s.after_tax), "fraction"),
            "marginal_tax_rate": qty(h.tax_rate, "fraction"),
            "discounting": {"t0_column": "Y0", "convention": "end_of_year", "source": src},
            "tax_summary": (
                "Marginal rate on revenue less operating cost less straight-line "
                "depreciation; parametric schedule (ADR 0051)."
                if h.basis == "after-tax"
                else "Study reports pre-tax figures only; tax modelled at the stated "
                "regime rate on revenue less operating cost less straight-line "
                "depreciation (ADR 0054)."
            ),
        },
        "status": {
            "permitted": False,
            "financed": False,
            "construction_decision": False,
            "source": src,
        },
        "schedule": {
            "periods": [f"Y{i}" for i in range(n)],
            "money_units": "US$ millions",
            "columns": {
                "payable_gold_koz": col(s.payable_koz),
                "gold_revenue": col(s.gold_revenue),
                "taxes": col(s.taxes),
                "initial_capex": col(s.initial_capex),
                "cash_flow_pre_tax": col(s.pre_tax),
                "cash_flow_after_tax": col(s.after_tax),
            },
        },
        "notes": f"Parametric schedule: cost factor {s.cost_factor:.4f}, tilt {s.tilt:.4f}.",
    }
    return Case.model_validate(raw)
