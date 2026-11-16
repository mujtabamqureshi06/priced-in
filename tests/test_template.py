"""The case template matches the schema: filling only its keys gives a case that loads."""

from pathlib import Path
from typing import Any

import numpy as np
import pytest
import yaml

from pricedin.inputs import REQUIRED_COLUMNS, Case
from pricedin.project import discount_factors

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "cases" / "_template.yaml"


def _ref(location: str = "Table 1") -> dict[str, str]:
    return {"document": "study", "location": location}


def _q(value: float, units: str) -> dict[str, Any]:
    return {"value": value, "units": units, "source": _ref()}


def _column(values: list[float]) -> dict[str, Any]:
    return {"values": values, "total": float(sum(values)), "source": _ref()}


def _filled() -> dict[str, Any]:
    """A two-period toy project written against the template's keys only."""
    revenue = [0.0, 1000.0]
    royalty = [0.0, 20.0]
    capex = [500.0, 0.0]
    pre_tax = [-500.0, 680.0]
    taxes = [0.0, 100.0]
    after_tax = [p - t for p, t in zip(pre_tax, taxes, strict=True)]
    after_tax_npv = after_tax[0] + after_tax[1] / 1.05
    return {
        "id": "toy_case",
        "name": "Toy project",
        "operator": "Example Corp.",
        "jurisdiction": "Nevada, United States",
        "commodity": "gold",
        "currency": "USD",
        "as_of": "2024-01-01",
        "operator_share": 1.0,
        "documents": [
            {
                "id": "study",
                "title": "Toy feasibility study",
                "issuer": "Example Corp.",
                "date": "2023-06-01",
                "url": "https://example.com/study.pdf",
            }
        ],
        "study": {
            "stage": "FS",
            "document": "study",
            "effective_date": "2023-06-01",
            "price_deck": {"gold": _q(2000.0, "US$/oz")},
            "discount_rate": _q(0.05, "fraction per year"),
            "npv_pre_tax": _q(pre_tax[0] + pre_tax[1] / 1.05, "US$ thousands"),
            "npv_after_tax": _q(after_tax_npv, "US$ thousands"),
            "irr_after_tax": _q(0.16, "fraction per year"),
            "marginal_tax_rate": _q(0.25, "fraction of change in pre-tax profit"),
            "discounting": {"t0_column": "Year 0", "convention": "end_of_year", "source": _ref()},
            "tax_summary": "Federal tax 21% and a state tax, Section 22.",
        },
        "status": {
            "permitted": False,
            "financed": False,
            "construction_decision": False,
            "source": _ref("Section 20"),
        },
        "schedule": {
            "money_units": "US$ thousands",
            "revenue_linked": ["existing_royalties"],
            "periods": ["Year 0", "Year 1"],
            "columns": {
                "payable_gold_koz": _column([0.0, 0.5]),
                "revenue": _column(revenue),
                "gold_revenue": _column(revenue),
                "existing_royalties": _column(royalty),
                "operating_cost": _column([0.0, 300.0]),
                "initial_capex": _column(capex),
                "taxes": _column(taxes),
                "cash_flow_pre_tax": _column(pre_tax),
                "cash_flow_after_tax": _column(after_tax),
            },
        },
    }


def test_template_keys_match_the_schema() -> None:
    template = yaml.safe_load(TEMPLATE.read_text(encoding="utf-8"))
    assert set(template) == set(Case.model_fields)
    assert set(template["study"]) == set(Case.model_fields["study"].annotation.model_fields)  # type: ignore[union-attr]
    assert set(template["schedule"]) == set(
        Case.model_fields["schedule"].annotation.model_fields  # type: ignore[union-attr]
    )


def test_template_lists_every_required_column() -> None:
    text = TEMPLATE.read_text(encoding="utf-8")
    for column in REQUIRED_COLUMNS:
        assert column in text


def test_a_case_filled_from_the_template_loads() -> None:
    template = yaml.safe_load(TEMPLATE.read_text(encoding="utf-8"))
    filled = _filled()
    assert set(filled) <= set(template)
    case = Case.model_validate(filled)
    flows = np.asarray(case.schedule.columns["cash_flow_after_tax"].values)
    assert float(flows @ discount_factors(case, 0.05)) == pytest.approx(
        case.study.npv_after_tax.value
    )
