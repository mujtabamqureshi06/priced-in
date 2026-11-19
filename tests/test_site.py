"""The website's home page: the export's rules, and every page number equal to the export."""

from __future__ import annotations

import importlib.util
import json
import re
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


export_mod = _load("export_site_example", ROOT / "scripts" / "export_site_example.py")
build_mod = _load("site_build", ROOT / "site" / "build.py")


@lru_cache(maxsize=1)
def _export() -> dict[str, Any]:
    # A small run keeps the test fast; the published page uses the default 200,000 paths.
    data: dict[str, Any] = export_mod.export(n_paths=4_000, seed=1)
    return data


@pytest.fixture(scope="module")
def data() -> dict[str, Any]:
    return _export()


@pytest.fixture(scope="module")
def page(tmp_path_factory: pytest.TempPathFactory, data: dict[str, Any]) -> str:
    tmp = tmp_path_factory.mktemp("site")
    path = tmp / "example.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    out = build_mod.build(path, tmp / "_site")
    text: str = out.read_text(encoding="utf-8")
    return text


class _Text(HTMLParser):
    """Collect visible text and the text of elements carrying ``data-k``."""

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.bound: dict[str, list[str]] = {}
        self._stack: list[str | None] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self._skip += 1
        if tag in ("br", "input", "meta", "link", "img"):
            return
        self._stack.append(dict(attrs).get("data-k"))

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self._skip -= 1
        if tag in ("br", "input", "meta", "link", "img"):
            return
        if self._stack:
            self._stack.pop()

    def handle_data(self, text: str) -> None:
        if self._skip:
            return
        self.parts.append(text)
        keys = [k for k in self._stack if k]
        if keys and text.strip():
            self.bound.setdefault(keys[-1], []).append(text.strip())


def _parse(page: str) -> _Text:
    p = _Text()
    p.feed(page)
    return p


def _visible(page: str) -> str:
    return re.sub(r"\s+", " ", " ".join(_parse(page).parts))


# ---------------------------------------------------------------- the export


def test_export_reproduces_the_study(data: dict[str, Any]) -> None:
    assert data["study_npv_check"] == pytest.approx(250.0, abs=0.05)


def test_odds_cover_every_control_state(data: dict[str, Any]) -> None:
    c = data["controls"]
    keys = {
        f"{p}_{g}_{r}_{o}"
        for p in c["prices"]
        for g in c["golds"]
        for r in c["returns"]
        for o in (0, 1)
    }
    assert set(data["odds"]) == keys
    assert len(keys) == 120


def test_odds_are_price_over_the_shown_value(data: dict[str, Any]) -> None:
    for key, odds in data["odds"].items():
        price, cell = key.split("_", 1)
        value = data["value_m"][cell]
        assert abs(value - data["grid"][cell]["v"]) <= 0.55
        if int(price) > value:
            assert odds is None, key
        else:
            assert odds == export_mod.whole(100 * int(price) / value), key
            assert 0 < odds <= 100


def test_rounding_is_half_up() -> None:
    assert export_mod.whole(52.5) == 53
    assert export_mod.whole(52.49) == 52
    assert export_mod.whole(-44.5) == -44
    assert export_mod.implied_odds(120, 228.55) == 52  # shown value is US$229M
    assert export_mod.implied_odds(230, 228.55) is None


def test_bridge_steps_add_up(data: dict[str, Any]) -> None:
    b = data["bridge_steps"]
    assert b["study"] + b["market"] + b["overruns"] + b["return"] == b["worth_if_built"]
    assert b["worth_if_built"] == data["value_m"]["2000_10_1"]


def test_sensitivity_base_is_the_starting_odds(data: dict[str, Any]) -> None:
    assert data["sensitivity"]["base"] == data["odds"]["120_2000_10_1"]
    assert len(data["sensitivity"]["rows"]) == 5


def test_drawn_paths_carry_the_engine_draws(data: dict[str, Any]) -> None:
    assert len(data["paths"]) == len(data["gate_draws"]) == 40
    assert all(0 <= x < 1 for x in data["gate_draws"])
    assert all(
        len(p) == 13 and p[0] == data["inputs"]["gold_spot_usd_per_oz"] for p in data["paths"]
    )


def test_gold_figures_scale_with_the_gold_price(data: dict[str, Any]) -> None:
    f = data["gold_figures"]
    assert f["2200"]["median"] == pytest.approx(f["2000"]["median"] * 1.1, abs=1)
    assert f["1800"]["p95"] == pytest.approx(f["2000"]["p95"] * 0.9, abs=1)


def test_overrun_histogram_is_a_distribution(data: dict[str, Any]) -> None:
    assert sum(data["overrun_hist"]["share"]) == pytest.approx(100, abs=0.7)


# ---------------------------------------------------------------- the page


def _check_numbers(page: str, data: dict[str, Any]) -> None:
    p = _parse(page)
    key0 = "2000_10_1"
    odds0 = data["odds"][f"120_{key0}"]
    v0 = data["value_m"][key0]
    assert set(p.bound["price"]) == {"US$120M"}
    assert set(p.bound["value"]) == {f"US${v0}M"}
    assert set(p.bound["odds"]) == {f"{odds0}%"}
    assert set(p.bound["oddsn"]) == {str(odds0)}
    g = data["gold_figures"]["2000"]
    assert p.bound["g50"] == [f"US${g['median']:,}"]
    assert p.bound["g90"] == [f"US${g['p5']:,} to US${g['p95']:,}"]
    assert page.count('class="pi-d on"') == odds0
    lit = sum(1 for d in data["gate_draws"] if d * 100 < odds0)
    assert page.count('class="pi-pg on"') == lit
    _check_tables(page, data)
    m = re.search(r'<script type="application/json" id="pi-data">(.*?)</script>', page, re.S)
    assert m is not None
    embedded = json.loads(m.group(1))
    assert embedded["odds"] == data["odds"]
    assert embedded["value_m"] == data["value_m"]
    assert embedded["gold_figures"] == data["gold_figures"]


def _check_tables(page: str, data: dict[str, Any]) -> None:
    text = _visible(page)
    h = data["inputs"]["headline"]
    assert f"Cost to build US${h['initial_capex_usd_m']:.0f}M" in text
    assert f"Engine, same assumptions US${data['study_npv_check']:.1f}M" in text
    b = data["bridge_steps"]
    for step in (b["market"], b["overruns"], b["return"]):
        assert (f"+{step}" if step >= 0 else "\u2212" + str(abs(step))) in text
    assert f"Worth if built {b['worth_if_built']}" in text
    for row in data["sensitivity"]["rows"]:
        lo, hi = sorted((row["a"], row["b"]))
        assert f"{lo}%" in text and f"{hi}%" in text
    ov = data["overrun_summary"]
    assert f"costs {ov['mean_pct']}% more" in text
    assert f"{data['meta']['n_paths']:,} possible outcomes" in text


def test_page_numbers_equal_the_export(page: str, data: dict[str, Any]) -> None:
    _check_numbers(page, data)


BUILT = ROOT / "site" / "_site"


@pytest.mark.skipif(not (BUILT / "index.html").exists(), reason="site not built")
def test_built_site_equals_its_export() -> None:
    """The page that is published matches the full-run export it was built from."""
    page = (BUILT / "index.html").read_text(encoding="utf-8")
    data = json.loads((BUILT / "example.json").read_text(encoding="utf-8"))
    _check_numbers(page, data)
    test_page_wording_rules(page)
    test_page_makes_no_third_party_requests(page)


def test_page_wording_rules(page: str) -> None:
    text = _visible(page).lower()
    assert "—" not in page
    for word in ("futures", "fair", " bet ", "probability", "the market's odds"):
        assert word not in text, word
    assert "implied odds of a build on schedule" in text
    assert "gold prices used for valuation, not a forecast" in text


def test_page_makes_no_third_party_requests(page: str) -> None:
    for attr in re.findall(r'(?:src|href)="([^"]+)"', page):
        if attr.startswith(("#", "assets/", "data:")):
            continue
        # External links are plain navigation, never loaded resources.
        assert attr.startswith(("https://github.com/", "https://www.linkedin.com/")), attr
    assert not re.search(r'<(?:script|link|img)[^>]+(?:src|href)="https?://', page)
