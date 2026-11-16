import copy
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from pricedin.inputs import Case, StudyStage, load_case

CASES = Path(__file__).resolve().parents[1] / "cases"


def _npv(values: tuple[float, ...], rate: float, t0: int) -> float:
    return sum(v / (1 + rate) ** (i - t0) for i, v in enumerate(values))


@pytest.fixture
def south_railroad_raw() -> dict[str, Any]:
    raw: dict[str, Any] = yaml.safe_load(
        (CASES / "south_railroad.yaml").read_text(encoding="utf-8")
    )
    return raw


def test_south_railroad_loads() -> None:
    case = load_case(CASES / "south_railroad.yaml")
    assert case.study.stage is StudyStage.PFS
    assert len(case.schedule.periods) == 12


@pytest.mark.parametrize(
    ("column", "npv_field"),
    [
        ("cash_flow_after_tax", "npv_after_tax"),
        ("cash_flow_pre_tax", "npv_pre_tax"),
    ],
)
def test_south_railroad_reproduces_study_npv(column: str, npv_field: str) -> None:
    """Transcription check: the table must reproduce the published NPV to the dollar."""
    case = load_case(CASES / "south_railroad.yaml")
    t0 = case.schedule.periods.index(case.study.discounting.t0_column)
    npv = _npv(case.schedule.columns[column].values, case.study.discount_rate.value, t0)
    published = getattr(case.study, npv_field).value
    assert npv == pytest.approx(published, abs=1.0)


def test_south_railroad_cash_flow_identity() -> None:
    """Pre-tax cash flow = revenue - costs + working capital - capex, period by period."""
    c = load_case(CASES / "south_railroad.yaml").schedule.columns
    for i, reported in enumerate(c["cash_flow_pre_tax"].values):
        derived = (
            c["revenue"].values[i]
            - c["operating_cost"].values[i]
            - c["existing_royalties"].values[i]
            - c["salvage"].values[i]
            - c["reclamation"].values[i]
            + c["working_capital"].values[i]
            - c["initial_capex"].values[i]
            - c["expansion_capex"].values[i]
            - c["sustaining_capex"].values[i]
        )
        assert derived == pytest.approx(reported, abs=2.0), f"period {i}"
        after = reported - c["taxes"].values[i]
        assert after == pytest.approx(c["cash_flow_after_tax"].values[i], abs=2.0)


def test_rejects_wrong_total(south_railroad_raw: dict[str, Any]) -> None:
    raw = copy.deepcopy(south_railroad_raw)
    raw["schedule"]["columns"]["payable_gold_koz"]["values"][1] = 103
    with pytest.raises(ValidationError, match="check the transcription"):
        Case.model_validate(raw)


def test_rejects_ragged_column(south_railroad_raw: dict[str, Any]) -> None:
    raw = copy.deepcopy(south_railroad_raw)
    raw["schedule"]["columns"]["taxes"]["values"].append(0)
    raw["schedule"]["columns"]["taxes"]["total"] = None
    with pytest.raises(ValidationError, match="13 values but there are 12 periods"):
        Case.model_validate(raw)


def test_rejects_missing_required_column(south_railroad_raw: dict[str, Any]) -> None:
    raw = copy.deepcopy(south_railroad_raw)
    del raw["schedule"]["columns"]["cash_flow_after_tax"]
    with pytest.raises(ValidationError, match="missing required columns"):
        Case.model_validate(raw)


def test_rejects_unknown_document(south_railroad_raw: dict[str, Any]) -> None:
    raw = copy.deepcopy(south_railroad_raw)
    raw["study"]["discount_rate"]["source"]["document"] = "fs_2022"
    with pytest.raises(ValidationError, match="unknown document 'fs_2022'"):
        Case.model_validate(raw)


def test_rejects_look_ahead(south_railroad_raw: dict[str, Any]) -> None:
    raw = copy.deepcopy(south_railroad_raw)
    raw["documents"].append(
        {
            "id": "fs_2022",
            "title": "Feasibility Study",
            "issuer": "GSV",
            "date": "2022-02-23",
            "url": "https://example.org",
        }
    )
    with pytest.raises(ValidationError, match="no look-ahead"):
        Case.model_validate(raw)


def test_rejects_royalty_rate_above_one(south_railroad_raw: dict[str, Any]) -> None:
    raw = copy.deepcopy(south_railroad_raw)
    raw["royalties"][0]["rate"]["value"] = 0.633
    Case.model_validate(raw)
    raw["royalties"][0]["rate"]["value"] = 63.3
    with pytest.raises(ValidationError, match="fraction in"):
        Case.model_validate(raw)


# Tolerance for reproducing the published NPV, in the case's money units. South Railroad
# reports whole US$ thousands; Osino rounds each cell to whole US$ millions, so the sum
# of 15 discounted cells can differ from the published NPV by up to about US$2M.
NPV_TOLERANCE = {"south_railroad": 1.0, "osino_twin_hills": 2.0}


@pytest.mark.parametrize("case_id", sorted(NPV_TOLERANCE))
@pytest.mark.parametrize(
    ("column", "npv_field"),
    [("cash_flow_after_tax", "npv_after_tax"), ("cash_flow_pre_tax", "npv_pre_tax")],
)
def test_every_case_reproduces_its_study_npv(case_id: str, column: str, npv_field: str) -> None:
    case = load_case(CASES / f"{case_id}.yaml")
    t0 = case.schedule.periods.index(case.study.discounting.t0_column)
    npv = _npv(case.schedule.columns[column].values, case.study.discount_rate.value, t0)
    assert npv == pytest.approx(getattr(case.study, npv_field).value, abs=NPV_TOLERANCE[case_id])


def test_osino_residual_nets_to_about_zero() -> None:
    """Rows shown in DFS Table 22.3.2 explain pre-tax cash flow up to a residual that
    nets to about zero over life (working capital); see the case notes."""
    c = load_case(CASES / "osino_twin_hills.yaml").schedule.columns
    residual = [
        c["cash_flow_pre_tax"].values[i]
        - (
            c["revenue"].values[i]
            - c["government_royalty_and_levy"].values[i]
            - c["selling_and_marketing"].values[i]
            - c["operating_cost"].values[i]
            - c["initial_capex"].values[i]
            - c["sustaining_capex"].values[i]
        )
        for i in range(len(c["revenue"].values))
    ]
    assert residual[1] == pytest.approx(10.7, abs=0.05)
    assert sum(residual) == pytest.approx(0.0, abs=2.0)
    for i, pre in enumerate(c["cash_flow_pre_tax"].values):
        assert pre - c["taxes"].values[i] == pytest.approx(
            c["cash_flow_after_tax"].values[i], abs=1.0
        )
