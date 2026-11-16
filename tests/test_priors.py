from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from pricedin.priors import Prior, Status, load_priors


def _entry(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": "capex.overrun.fs",
        "description": "Capital cost outcome as a multiple of the FS estimate",
        "distribution": {"kind": "shifted_lognormal", "mu": 0.0, "sigma": 0.3, "shift": 0.0},
        "units": "multiple of FS initial capex",
        "source": "Bertisen and Davis (2008)",
        "location": "The Engineering Economist 53(2):118-139",
        "status": "V-abs",
    }
    base.update(overrides)
    return base


def _write(tmp_path: Path, entries: list[dict[str, Any]]) -> Path:
    path = tmp_path / "priors.yaml"
    path.write_text(yaml.safe_dump({"priors": entries}), encoding="utf-8")
    return path


def test_loads_valid_entry(tmp_path: Path) -> None:
    registry = load_priors(_write(tmp_path, [_entry()]))
    prior = registry.get("capex.overrun.fs")
    assert prior.status is Status.VERIFIED_ABSTRACT
    assert prior.distribution.kind == "shifted_lognormal"


@pytest.mark.parametrize("missing", ["source", "units", "location", "status"])
def test_rejects_entry_missing_required_field(missing: str) -> None:
    entry = _entry()
    del entry[missing]
    with pytest.raises(ValidationError, match=missing):
        Prior.model_validate(entry)


@pytest.mark.parametrize("field", ["source", "units", "location"])
def test_rejects_empty_required_text(field: str) -> None:
    with pytest.raises(ValidationError, match=field):
        Prior.model_validate(_entry(**{field: ""}))


def test_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError, match="status"):
        Prior.model_validate(_entry(status="verified"))


def test_secondary_source_must_be_flagged() -> None:
    with pytest.raises(ValidationError, match="must set a flag"):
        Prior.model_validate(_entry(status="S"))
    assert Prior.model_validate(_entry(status="S", flag="secondary source only")).flagged


def test_rejects_duplicate_ids(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="duplicate prior id"):
        load_priors(_write(tmp_path, [_entry(), _entry()]))


def test_rejects_file_without_priors_list(tmp_path: Path) -> None:
    path = tmp_path / "priors.yaml"
    path.write_text("other: 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="top-level 'priors' list"):
        load_priors(path)


def test_unknown_id_error_names_the_id(tmp_path: Path) -> None:
    registry = load_priors(_write(tmp_path, [_entry()]))
    with pytest.raises(KeyError, match=r"stage\.fs_to_build"):
        registry.get("stage.fs_to_build")


@pytest.mark.parametrize(
    "dist",
    [
        {"kind": "uniform", "low": 0.9, "high": 0.3},
        {"kind": "triangular", "low": 0.3, "mode": 0.99, "high": 0.95},
        {"kind": "shifted_lognormal", "mu": 0.0, "sigma": 0.0},
        {"kind": "beta", "a": 1.0, "b": 1.0},
    ],
)
def test_rejects_invalid_distributions(dist: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        Prior.model_validate(_entry(distribution=dist))


def test_flagged_lists_only_flagged_priors(tmp_path: Path) -> None:
    entries = [
        _entry(),
        _entry(id="stage.fs_to_build", status="S", flag="secondary source only"),
    ]
    registry = load_priors(_write(tmp_path, entries))
    assert [p.id for p in registry.flagged()] == ["stage.fs_to_build"]


def test_alternative_without_status_must_be_judgment() -> None:
    bad = {"label": "stress low", "value": 0.5, "source": "AMC"}
    with pytest.raises(ValidationError, match="judgment"):
        Prior.model_validate(_entry(sensitivity=[bad]))
    good = {"label": "stress low", "value": 0.5, "source": "judgment"}
    assert Prior.model_validate(_entry(sensitivity=[good])).sensitivity[0].value == 0.5


def test_repository_registry_is_valid() -> None:
    registry = load_priors(Path(__file__).resolve().parents[1] / "data" / "priors.yaml")
    fs = registry.get("stage.fs_to_build")
    assert fs.distribution.kind == "fixed"
    assert {a.value for a in fs.sensitivity} == {0.75, 0.5, 0.95}
    assert all(p.flagged for p in registry.priors.values() if p.id.startswith("stage."))


def test_overrun_prior_reproduces_published_moments() -> None:
    """Bertisen and Davis (2008) report the lognormal part as mean 0.35, SD 0.42."""
    import math

    registry = load_priors(Path(__file__).resolve().parents[1] / "data" / "priors.yaml")
    dist = registry.get("capex.overrun.fs").distribution
    assert dist.kind == "shifted_lognormal"
    mean = math.exp(dist.mu + dist.sigma**2 / 2)
    sd = mean * math.sqrt(math.exp(dist.sigma**2) - 1)
    assert mean == pytest.approx(0.35, abs=5e-6)
    assert sd == pytest.approx(0.42, abs=5e-6)
    assert dist.shift == 0.91


def test_pfs_overrun_uses_fs_distribution_with_flag() -> None:
    registry = load_priors(Path(__file__).resolve().parents[1] / "data" / "priors.yaml")
    fs = registry.get("capex.overrun.fs").distribution
    pfs = registry.get("capex.overrun.pfs")
    assert pfs.distribution == fs
    assert "understates PFS cost risk" in pfs.flag


def test_pfs_sensitivity_keeps_mean_and_widens_sd() -> None:
    """ADR 0015: sensitivity B holds the lognormal mean at 0.35 and widens the SD to 0.70."""
    import math

    mu, sigma = -1.854541, 1.268636
    mean = math.exp(mu + sigma**2 / 2)
    sd = mean * math.sqrt(math.exp(sigma**2) - 1)
    assert mean == pytest.approx(0.35, abs=5e-6)
    assert sd == pytest.approx(0.70, abs=5e-6)


def test_ramp_up_weights_match_mcnulty_table_2() -> None:
    registry = load_priors(Path(__file__).resolve().parents[1] / "data" / "priors.yaml")
    counts = {1: 23, 2: 5, 3: 6, 4: 7}
    weights = {}
    for series, n in counts.items():
        dist = registry.get(f"rampup.weight.series{series}").distribution
        assert dist.kind == "fixed"
        weights[series] = dist.value
        assert dist.value == pytest.approx(n / 41, abs=1e-6)
    assert sum(weights.values()) == pytest.approx(1.0, abs=1e-6)


def test_ramp_up_curves_are_complete_and_ordered() -> None:
    import csv

    path = Path(__file__).resolve().parents[1] / "data" / "ramp_up_mcnulty_1998.csv"
    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    curve: dict[int, dict[int, float]] = {}
    for r in rows:
        curve.setdefault(int(r["series"]), {})[int(r["months_since_commissioning"])] = float(
            r["percent_of_design_capacity"]
        )
    assert set(curve) == {1, 2, 3, 4}
    for s in curve.values():
        assert sorted(s) == [6, 12, 18, 24, 30, 36]
        values = [s[m] for m in sorted(s)]
        assert values == sorted(values)
    for m in (6, 12, 18, 24, 30, 36):
        assert curve[1][m] > curve[2][m] > curve[3][m] > curve[4][m]


def test_oxide_class_weights_match_table_2() -> None:
    registry = load_priors(Path(__file__).resolve().parents[1] / "data" / "priors.yaml")
    s1 = registry.get("rampup.weight.oxide.series1").distribution
    s2 = registry.get("rampup.weight.oxide.series2").distribution
    assert s1.kind == "fixed" and s2.kind == "fixed"
    assert s1.value == pytest.approx(6 / 7, abs=1e-6)
    assert s2.value == pytest.approx(1 / 7, abs=1e-6)
    assert s1.value + s2.value == pytest.approx(1.0, abs=1e-6)


def test_judgment_status_requires_decision_and_flag() -> None:
    from pricedin.priors import Prior

    base = {
        "id": "x.y",
        "description": "d",
        "distribution": {"kind": "fixed", "value": 1.0},
        "units": "years",
        "source": "judgment",
        "location": "ADR 0000",
        "status": "J",
    }
    with pytest.raises(ValueError, match="status J"):
        Prior.model_validate(base)
    with pytest.raises(ValueError, match="status J"):
        Prior.model_validate({**base, "flag": "f", "decision": "ADR 9999", "source": "a paper"})
    ok = Prior.model_validate({**base, "flag": "f", "decision": "ADR 9999"})
    assert ok.flagged
