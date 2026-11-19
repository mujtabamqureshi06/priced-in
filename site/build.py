"""Build the website's home page from the engine export.

Reads ``site/data/example.json`` (written by ``scripts/export_site_example.py``) and
writes a static site to ``site/_site/``. Every figure on the page is taken from the
export: this script formats numbers and draws charts, and the page's script
(``site/src/home.js``) only looks values up and draws. Neither computes a published
number.

Usage: uv run python site/build.py [--data site/data/example.json] [--out site/_site]
"""

from __future__ import annotations

import argparse
import html
import json
import math
import random
import shutil
from pathlib import Path
from typing import Any

SITE = Path(__file__).resolve().parent
REPO_URL = "https://github.com/mujtabamqureshi06/priced-in"
LINKS = {
    "deals": f"{REPO_URL}#results-so-far",
    "read": f"{REPO_URL}#what-it-does",
    "code": REPO_URL,
    "credit": "https://www.linkedin.com/in/mujtabamoeen/",
}
WORDS = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
}

# Gold fan chart geometry (SVG units): 12 years, axis US$400 to US$6,600.
FAN_W, FAN_H, FAN_YMAX, FAN_YMIN = 640, 260, 6600, 400
# Cash-flow chart geometry (SVG units), US$M.
CF_W, CF_H, CF_TOP, CF_BOT = 520, 190, 110.0, -170.0


def usd_m(x: int | float) -> str:
    """Format US$ millions as on the page: US$229M."""
    return f"US${x:,.0f}M" if float(x).is_integer() else f"US${x:,.1f}M"


def usd(x: int | float) -> str:
    """Format a US$ amount with thousands separators: US$2,084."""
    return f"US${x:,.0f}"


def pct(x: float) -> str:
    """Format a fraction as a whole or one-decimal percent: 0.015 -> 1.5%."""
    v = x * 100
    return f"{v:.0f}%" if abs(v - round(v)) < 1e-9 else f"{v:.1f}%"


def signed(x: int) -> str:
    """Format a bridge step with a plus or a minus sign (U+2212)."""
    return f"+{x}" if x >= 0 else f"−{abs(x)}"


def esc(text: str) -> str:
    """Escape text for HTML."""
    return html.escape(text, quote=True)


# ---------------------------------------------------------------- background drawing


def contours(
    w: int,
    h: int,
    cx: int,
    cy: int,
    stroke: str,
    base: float,
    n: int = 11,
    step: int = 62,
    aspect: float = 1.35,
) -> str:
    """Draw decorative contour lines around a centre."""
    out = []
    for k in range(n):
        r = 70 + k * step
        pts = []
        for a in range(0, 361, 6):
            t = math.radians(a)
            rr = r * (
                1
                + 0.10 * math.sin(3 * t + k * 0.5)
                + 0.06 * math.sin(5 * t - k * 0.8)
                + 0.04 * math.cos(2 * t + k)
            )
            pts.append(f"{cx + rr * math.cos(t) * aspect:.0f},{cy + rr * math.sin(t):.0f}")
        wgt = 1.8 if k % 4 == 0 else 1.1
        op = max(base - k * base / (n + 6), 0.04)
        out.append(
            f'<polygon points="{" ".join(pts)}" fill="none" stroke="{stroke}" '
            f'stroke-opacity="{op:.3f}" stroke-width="{wgt}"></polygon>'
        )
    return (
        f'<svg class="pi-topo" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" '
        f'aria-hidden="true" focusable="false">{"".join(out)}</svg>'
    )


def survey(
    w: int,
    h: int,
    stroke: str,
    op: float,
    seed: int,
    *,
    north: tuple[int, int] | None = None,
    scale: tuple[int, int] | None = None,
    section: tuple[tuple[int, int], tuple[int, int]] | None = None,
    road: str | None = None,
    holes: int = 14,
    grid: int = 170,
) -> str:
    """Draw mine-plan marks: survey ticks, drill-hole collars, a haul road, a section line."""
    rnd = random.Random(seed)
    o = []
    for gx in range(grid // 2, w, grid):
        for gy in range(grid // 2, h, grid):
            o.append(
                f'<path d="M{gx - 6} {gy}H{gx + 6}M{gx} {gy - 6}V{gy + 6}" stroke="{stroke}" '
                f'stroke-opacity="{op * 0.8:.2f}" stroke-width="1"></path>'
            )
    for _ in range(holes):
        x, y = rnd.randint(40, w - 40), rnd.randint(40, h - 40)
        o.append(
            f'<circle cx="{x}" cy="{y}" r="4" fill="none" stroke="{stroke}" '
            f'stroke-opacity="{op:.2f}" stroke-width="1.2"></circle>'
            f'<path d="M{x - 8} {y}H{x + 8}M{x} {y - 8}V{y + 8}" stroke="{stroke}" '
            f'stroke-opacity="{op:.2f}" stroke-width="1"></path>'
        )
    if road:
        o.append(
            f'<path d="{road}" fill="none" stroke="{stroke}" stroke-opacity="{op * 0.45:.2f}" '
            f'stroke-width="7" stroke-linecap="round"></path>'
            f'<path d="{road}" fill="none" stroke="{stroke}" stroke-opacity="{op * 1.2:.2f}" '
            f'stroke-width="1" stroke-dasharray="9 7"></path>'
        )
    if section:
        (x1, y1), (x2, y2) = section
        o.append(
            f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{stroke}" stroke-opacity="{op * 1.2:.2f}" '
            f'stroke-width="1.2" stroke-dasharray="14 5 3 5"></path>'
            f'<circle cx="{x1}" cy="{y1}" r="3.5" fill="{stroke}" fill-opacity="{op * 1.2:.2f}"></circle>'
            f'<circle cx="{x2}" cy="{y2}" r="3.5" fill="{stroke}" fill-opacity="{op * 1.2:.2f}"></circle>'
            f'<text x="{x1 - 16}" y="{y1 + 5}" font-family="Inter, sans-serif" font-size="13" '
            f'font-weight="700" fill="{stroke}" fill-opacity="{op * 1.5:.2f}">A</text>'
            f'<text x="{x2 + 9}" y="{y2 + 5}" font-family="Inter, sans-serif" font-size="13" '
            f'font-weight="700" fill="{stroke}" fill-opacity="{op * 1.5:.2f}">A′</text>'
        )
    if north:
        x, y = north
        o.append(
            f'<path d="M{x} {y - 26}L{x + 9} {y + 10}L{x} {y + 3}L{x - 9} {y + 10}Z" fill="none" '
            f'stroke="{stroke}" stroke-opacity="{op * 1.5:.2f}" stroke-width="1.4"></path>'
            f'<text x="{x}" y="{y - 32}" text-anchor="middle" font-family="Inter, sans-serif" '
            f'font-size="13" font-weight="700" fill="{stroke}" fill-opacity="{op * 1.6:.2f}">N</text>'
        )
    if scale:
        x, y = scale
        o.append(
            f'<path d="M{x} {y}H{x + 120}M{x} {y - 5}V{y + 5}M{x + 60} {y - 5}V{y + 5}'
            f'M{x + 120} {y - 5}V{y + 5}" stroke="{stroke}" stroke-opacity="{op * 1.5:.2f}" '
            f'stroke-width="1.4"></path><rect x="{x}" y="{y - 3}" width="60" height="3" '
            f'fill="{stroke}" fill-opacity="{op * 1.3:.2f}"></rect>'
        )
    return (
        f'<svg class="pi-topo" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" '
        f'aria-hidden="true" focusable="false">{"".join(o)}</svg>'
    )


# ---------------------------------------------------------------- page parts


def tip(text: str, tip_id: str) -> str:
    """Return an "i" button with a tooltip tied to it for screen readers."""
    return (
        f'<span class="pi-tip"><button type="button" class="pi-i" aria-describedby="{tip_id}" '
        f'aria-label="What this means">i</button>'
        f'<span class="pi-tt" role="tooltip" id="{tip_id}">{esc(text)}</span></span>'
    )


def fan_chart(d: dict[str, Any], odds0: int | None) -> str:
    """Draw 40 engine price paths with the 5th to 95th percentile band and the median."""

    def xy(i: int, v: float) -> str:
        y = FAN_H - (min(v, FAN_YMAX) - FAN_YMIN) / (FAN_YMAX - FAN_YMIN) * FAN_H
        return f"{i * FAN_W / 12:.1f},{y:.1f}"

    q = d["q"]
    lines = []
    for k, (path, draw) in enumerate(zip(d["paths"], d["gate_draws"], strict=True)):
        pts = " ".join(xy(i, v) for i, v in enumerate(path))
        on = odds0 is not None and draw * 100 < odds0
        lines.append(
            f'<polyline class="pi-pb" pathLength="1" style="--k: {k}" points="{pts}"></polyline>'
        )
        lines.append(
            f'<polyline class="pi-pg{" on" if on else ""}" pathLength="1" style="--k: {k}" '
            f'data-draw="{draw}" points="{pts}"></polyline>'
        )
    band = (
        " ".join(xy(i, v) for i, v in enumerate(q[2]))
        + " "
        + " ".join(xy(i, q[0][i]) for i in range(12, -1, -1))
    )
    med = " ".join(xy(i, v) for i, v in enumerate(q[1]))

    def ty(v: int) -> float:
        return FAN_H - (v - FAN_YMIN) / (FAN_YMAX - FAN_YMIN) * FAN_H

    ticks = "".join(
        f'<line x1="0" x2="{FAN_W}" y1="{ty(v):.0f}" y2="{ty(v):.0f}" stroke="#DDE2E9"></line>'
        for v in (2000, 4000, 6000)
    )
    ylabels = "".join(
        f'<span class="pi-yl" style="top: {ty(v) / FAN_H * 100:.1f}%">{usd(v)}</span>'
        for v in (2000, 4000, 6000)
    )
    n_paths = d["meta"]["n_paths"]
    label = (
        f"{len(d['paths'])} of the {n_paths:,} simulated gold price paths over twelve years, "
        "with the middle path and the range that holds 90 percent of them. "
        "The paths drawn in gold are the outcomes that pass at the implied odds."
    )
    return (
        f'<div class="pi-chart" id="pi-fan"><svg viewBox="0 0 {FAN_W} {FAN_H}" width="100%" '
        f'style="display: block" role="img" aria-label="{esc(label)}">{ticks}'
        f'<g class="pi-fan"><polygon points="{band}" fill="#0F2747" fill-opacity="0.08"></polygon>'
        f'{"".join(lines)}<polyline points="{med}" fill="none" stroke="#0F2747" stroke-width="2" '
        f'stroke-dasharray="5 4"></polyline></g></svg>{ylabels}</div>'
        '<div class="pi-xl"><span>today</span><span>year 4</span><span>year 8</span>'
        "<span>year 12</span></div>"
    )


def cash_flow_chart(cf: list[float]) -> str:
    """Draw the study's after-tax cash flow by year."""

    def cy(v: float) -> float:
        return (CF_TOP - v) / (CF_TOP - CF_BOT) * CF_H

    step = CF_W / len(cf)
    bars = []
    for i, v in enumerate(cf):
        x, wdt = i * step + step * 0.16, step * 0.68
        y, hgt = (cy(v), cy(0) - cy(v)) if v >= 0 else (cy(0), cy(v) - cy(0))
        colour = "#0F2747" if v >= 0 else "#8A96A8"
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{wdt:.1f}" height="{hgt:.1f}" rx="3" '
            f'fill="{colour}"></rect>'
        )
    grid = "".join(
        f'<line x1="0" x2="{CF_W}" y1="{cy(v):.1f}" y2="{cy(v):.1f}" '
        f'stroke="{"#8A96A8" if v == 0 else "#E3E6EB"}" stroke-width="1"></line>'
        for v in (100, 0, -150)
    )
    ylab = "".join(
        f'<span class="pi-cyl" style="top: {cy(v) / CF_H * 100:.1f}%">{lab}</span>'
        for v, lab in ((100, "US$100M"), (0, "0"), (-150, "−US$150M"))
    )
    build = [v for v in cf if v < 0]
    prod = [v for v in cf if v >= 0]
    label = (
        f"Cash flow in the study by year: US${abs(build[0]):.0f} million spent in each of "
        f"{WORDS.get(len(build), str(len(build)))} building years, then income falling from "
        f"US${prod[0]:.0f} million to US${prod[-1]:.0f} million a year over {len(prod)} years "
        "of production."
    )
    return (
        '<div class="pi-cfw"><div class="pi-cfg"><div class="pi-chart" role="img" '
        f'aria-label="{esc(label)}"><svg viewBox="0 0 {CF_W} {CF_H}" width="100%" '
        f'style="display: block">{grid}{"".join(bars)}</svg></div>'
        f'<div class="pi-cyls">{ylab}</div></div>'
        f'<div class="pi-cxl">{"".join(f"<span>{i}</span>" for i in range(1, len(cf) + 1))}</div>'
        f'<p class="pi-cap">Year. {WORDS.get(len(build), str(len(build))).capitalize()} years '
        f"of building, then {WORDS.get(len(prod), str(len(prod)))} of production.</p></div>"
    )


def overrun_chart(d: dict[str, Any]) -> str:
    """Draw the capital cost ratios drawn in the base run."""
    oh = d["overrun_hist"]
    top = max(oh["share"])
    bars = "".join(
        f'<i style="height: {v / top * 100:.0f}%; background: {"#8A96A8" if e < 1.0 else "#0F2747"}"></i>'
        for e, v in zip(oh["edges"], oh["share"], strict=True)
    )
    s = d["overrun_summary"]
    label = (
        "Spread of build cost against the estimate in the study across the simulated outcomes. "
        f"On average the build costs {s['mean_pct']} percent more than planned; about "
        f"{s['double_or_more_in_100']} in 100 cost double or more."
    )
    n = len(oh["edges"])
    return (
        f'<div class="pi-ohw"><div class="pi-oh" role="img" aria-label="{esc(label)}">{bars}</div>'
        '<div class="pi-ohx"><span style="left: 0">−20%</span>'
        f'<span style="left: {2 / n * 100:.1f}%">as planned</span>'
        f'<span style="left: {7 / n * 100:.1f}%">+50%</span>'
        f'<span style="left: {12 / n * 100:.1f}%">double</span></div></div>'
        '<p class="pi-ohoff">Switched off: every outcome costs what the study said.</p>'
    )


def sensitivity_rows(d: dict[str, Any]) -> str:
    """Draw the implied odds range for each input moved alone."""
    base = d["sensitivity"]["base"]
    out = []
    for row in d["sensitivity"]["rows"]:
        a, b = row["a"], row["b"]
        if a is None or b is None:
            raise ValueError(f"sensitivity row {row['name']!r} has no solution at one end")
        lo, hi = min(a, b), max(a, b)
        label = f"{row['name']}: implied odds from {lo} to {hi} percent."
        out.append(
            f'<div class="pi-trow"><div class="nm">{esc(row["name"])}'
            f"<small>{esc(row['from'])} to {esc(row['to'])}</small></div>"
            f'<div class="pi-trk" role="img" aria-label="{esc(label)}">'
            f'<span class="rng" style="left: {lo * 0.92:.1f}%; width: {max(hi - lo, 0) * 0.92:.1f}%"></span>'
            f'<span class="base" style="left: {base * 0.92:.1f}%"></span>'
            f'<span class="lo" style="right: {100 - lo * 0.92 + 1.2:.1f}%">{lo}%</span>'
            f'<span class="hi" style="left: {hi * 0.92 + 1.2:.1f}%">{hi}%</span></div></div>'
        )
    return "".join(out)


def pills(
    name: str, legend: str, options: list[tuple[str, str]], default: str, help_html: str = ""
) -> str:
    """Return one radio group laid out as a row of equal-width buttons."""
    items = "".join(
        f'<input type="radio" name="{name}" id="{name}-{v}" value="{v}"'
        f'{" checked" if v == default else ""}><label for="{name}-{v}">{esc(text)}</label>'
        for v, text in options
    )
    return (
        f'<div class="pi-g" role="radiogroup" aria-labelledby="{name}-lab">'
        f'<span class="n" id="{name}-lab">{esc(legend)}{help_html}</span>'
        f'<div class="pi-pills">{items}</div></div>'
    )


def page_data(d: dict[str, Any], bar_scale: int) -> dict[str, Any]:
    """Return the lookup tables the page's script reads (no computation needed)."""
    return {
        "odds": d["odds"],
        "value_m": d["value_m"],
        "gold_figures": d["gold_figures"],
        "base_gold": d["inputs"]["gold_spot_usd_per_oz"],
        "bar_scale": bar_scale,
        "default": d["controls"]["default"],
    }


def build_page(d: dict[str, Any]) -> str:
    """Return the home page HTML."""
    c = d["controls"]
    dflt = c["default"]
    h = d["inputs"]["headline"]
    n_paths = d["meta"]["n_paths"]
    key0 = f"{dflt['gold']}_{dflt['return']}_{dflt['overrun']}"
    v0 = d["value_m"][key0]
    p0 = dflt["price"]
    odds0 = d["odds"][f"{p0}_{key0}"]
    if odds0 is None:
        raise ValueError("the starting settings must have a solution")
    g0 = d["gold_figures"][str(dflt["gold"])]
    bar_scale = math.ceil(max(d["value_m"].values()) / 50) * 50
    if bar_scale <= max(d["value_m"].values()):
        bar_scale += 50
    bs = d["bridge_steps"]
    if bs["study"] + bs["market"] + bs["overruns"] + bs["return"] != bs["worth_if_built"]:
        raise ValueError("bridge steps do not add up")
    sens = d["sensitivity"]
    if sens["base"] != odds0:
        raise ValueError("sensitivity base differs from the starting odds")
    ov = d["overrun_summary"]
    years_to_start = d["inputs"]["years_to_start"]
    dots_per = n_paths // 100
    study_rate = pct(h["study_discount_rate"])
    ret0 = f"{dflt['return']}%"
    se_text = f"Simulation error is at most {usd_m(d['se_max'])}."

    dots = "".join(f'<i class="pi-d{" on" if i < odds0 else ""}"></i>' for i in range(100))

    ctl = (
        pills("price", "Price paid", [(str(p), usd_m(p)) for p in c["prices"]], str(p0))
        + pills(
            "ret",
            "Extra return the buyer needs",
            [(str(r), f"{r}%") for r in c["returns"]],
            str(dflt["return"]),
            tip(
                "The extra yearly return the buyer requires on top of the risk-free rate, after "
                "inflation. A buyer who needs more will pay less for the same mine.",
                "tt-ret",
            ),
        )
        + pills(
            "ov",
            "Cost overruns",
            [("1", "as in past mines"), ("0", "none")],
            str(dflt["overrun"]),
            tip(
                "Drawn from the record of past mines (Bertisen and Davis, 2008). In the engine's "
                f"draws the build costs {ov['mean_pct']}% more than the study said on average, and "
                f"about {ov['double_or_more_in_100']} in 100 cost double or more. Switch this off "
                "to take the study at its word.",
                "tt-ov",
            ),
        )
        + pills(
            "gold", "Gold price today", [(str(g), usd(g)) for g in c["golds"]], str(dflt["gold"])
        )
    )

    data_json = json.dumps(page_data(d, bar_scale), separators=(",", ":")).replace("</", "<\\/")
    vw = v0 / bar_scale
    pw = p0 / bar_scale
    css = (SITE / "src" / "home.css").read_text(encoding="utf-8")
    meta = d["meta"]

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Priced In: the build odds in the price of an unbuilt mine</title>
<meta name="description" content="Priced In simulates {n_paths:,} possible outcomes for a mine, then works out what chance of construction makes a real price add up.">
<meta name="generator" content="pricedin {esc(meta["engine_version"])}, commit {esc(meta["commit"][:12])}, {n_paths} paths, seed {meta["seed"]}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E%3Crect width=%2732%27 height=%2732%27 rx=%277%27 fill=%27%230F2747%27/%3E%3Ccircle cx=%2716%27 cy=%2716%27 r=%277%27 fill=%27%23D9B15E%27/%3E%3C/svg%3E">
<link rel="preload" href="assets/fonts/inter-latin-wght.woff2" as="font" type="font/woff2" crossorigin>
<style>
body{{margin:0}}
a{{color:#0F2747}}a:hover{{color:#8A6417}}
{css}</style>
</head>
<body>
<div class="pi-root">
<a class="pi-skip" href="#example">Skip to the example</a>
<div class="pi-scope" style="--g: 1; --vw: {vw:.4f}; --pw: {pw:.4f}; --ob: {odds0 / 100:.2f}">

<div class="pi-hero">
{contours(1360, 900, 980, 150, "#5B7BAA", 0.5)}
{survey(1360, 900, "#7C9BC9", 0.30, 3, north=(104, 96), scale=(1150, 64), road="M-20 700 C 180 660, 300 600, 430 660 S 600 800, 700 880", holes=9)}
<header class="pi-wrap pi-nav">
<a href="#top" style="font-size: 21px; font-weight: 800; color: #FFFFFF; text-decoration: none; letter-spacing: -0.01em">Priced In</a>
<nav aria-label="Main"><a href="#how">How it works</a><a href="{LINKS["deals"]}">Real deals</a><a href="{LINKS["read"]}">How to read this site</a><details class="pi-menu"><summary>Menu</summary><div class="pi-menul"><a href="#how">How it works</a><a href="{LINKS["deals"]}">Real deals</a><a href="{LINKS["read"]}">How to read this site</a></div></details></nav>
</header>
<main id="top" class="pi-wrap pi-heroin">
<div class="pi-pitch">
<h1>Turn the price of an unbuilt mine into the odds it gets built.</h1>
<p>Priced In simulates {n_paths:,} possible outcomes for a mine, then works out what chance of construction makes a real price add up.</p>
<p style="display: flex; flex-wrap: wrap; gap: 12px; margin-top: 30px"><a class="pi-btn" href="#how">See how it works</a></p>
</div>

<section class="pi-machine" id="example" aria-label="Example mine">
<p class="pi-tag"><strong>Try it on an example mine</strong>Illustrative inputs. Every figure is computed by the engine.</p>
<div class="pi-given">
<div class="pi-fact"><span class="l">Its study says {tip("The value in the mine's engineering study: what it is worth if it is built on time and on budget, at the study's own gold price.", "tt-study")}</span><b>{usd_m(h["npv_after_tax_usd_m"])}</b></div>
<div class="pi-fact"><span class="l">A buyer pays {tip("A takeover offer for the whole mine. A share price or a royalty price can be read the same way.", "tt-price")}</span><b class="gold" data-k="price">{usd_m(p0)}</b></div>
<div class="pi-fact"><span class="l">Worth if built {tip("The average value to this buyer across the simulated outcomes in which the mine goes ahead, at the gold price, return and cost setting chosen below. " + se_text, "tt-value")}</span><b data-k="value">{usd_m(v0)}</b></div>
</div>
<div class="pi-out">
<div class="pi-grid" role="img" aria-label="The {n_paths:,} simulated outcomes drawn as 100 dots. Gold dots are the share that must end with the mine built for the price to match the value.">{dots}</div>
<div class="pi-read">
<div class="pi-ok"><p class="pi-big" data-k="odds">{odds0}%</p><p class="pi-lab">implied odds of a build on schedule</p><p class="pi-say">At a <span data-k="ret">{ret0}</span> extra return, the price matches the engine's value only if <span data-k="oddsn">{odds0}</span> of every 100 simulated outcomes end with the mine built on schedule.</p><p class="pi-eq">Price paid ÷ worth if built</p></div>
<div class="pi-ns"><p class="pi-big" style="font-size: 40px; color: #E6EBF2; line-height: 1.05">No odds are high enough</p><p class="pi-say">Even a certain build is worth less than the price at a <span data-k="ret">{ret0}</span> return. Odds alone do not explain this price.</p></div>
</div>
</div>
<p class="pi-sr" aria-live="polite" id="pi-live"></p>
<p class="pi-note">The engine works backwards from the price. It does not count how often the mine got built; it finds the share of simulated outcomes that must end in a built mine for the price to match its value. Each dot stands for {dots_per:,} of the {n_paths:,} outcomes.</p>
<div class="pi-ctl">{ctl}</div>
<p class="pi-demo"><strong>This mine is made up to show the method.</strong> The engine computed every figure from the inputs shown; none of it describes a real project. The answer moves a lot because it depends on what you assume, and that is the point.</p>
</section>
</main>
</div>

<div class="pi-light" style="position: relative">
{contours(1360, 2600, 180, 700, "#0F2747", 0.22, n=14, step=80, aspect=1.2)}
{contours(1360, 2600, 1500, 2150, "#0F2747", 0.16, n=7, step=70, aspect=1.2)}
{survey(1360, 2600, "#0F2747", 0.16, 7, section=((60, 1500), (1320, 1180)), road="M1380 300 C 1100 420, 1250 900, 900 1100 S 500 1280, 380 1420", holes=12, grid=190)}

<section id="how" class="pi-wrap" style="margin-top: -92px">
<div class="pi-card" style="padding: 30px 32px 30px 32px; text-align: center">
<h2 class="pi-h2" style="max-width: none">Where the number comes from</h2>
<p class="pi-sub" style="margin: 12px auto 0 auto; max-width: 860px">Not a guess: four steps, each one checkable. Change a setting above and steps 2 to 4 move with it.</p>
</div>
<div class="pi-steps">

<div class="pi-card">
<div class="pi-k"><span aria-hidden="true">1</span><h3>Start from the mine's own study</h3></div>
<p>The engine rebuilds the study's yearly cash flows and checks that it gets the study's value back before it changes anything.</p>
<div class="pi-tbl"><div><span>Cost to build</span><b>{usd_m(h["initial_capex_usd_m"])}</b></div><div><span>Gold produced</span><b>{h["payable_koz_per_year"] * 1000:,.0f} oz a year, {h["life_years"]} years</b></div><div><span>Cost per ounce</span><b>{usd(h["aisc_usd_per_oz"])}</b></div><div><span>Gold price in the study</span><b>{usd(h["gold_deck_usd_per_oz"])}</b></div><div><span>Tax rate</span><b>{pct(h["tax_rate"])}</b></div><div><span>Study value, at a {study_rate} discount rate</span><b>{usd_m(h["npv_after_tax_usd_m"])}</b></div><div><span>Engine, same assumptions</span><b>US${d["study_npv_check"]:.1f}M</b></div></div>
<p style="margin-top: 24px; font-size: 13px; font-weight: 700; color: #0F2747; text-align: center">Cash flow in the study, US$M a year</p>{cash_flow_chart(d["cf"])}
</div>

<div class="pi-card">
<div class="pi-k"><span aria-hidden="true">2</span><h3>Simulate {n_paths:,} outcomes</h3></div>
<p>In each one gold takes a different path, the build costs more or less than planned, and the mine goes ahead or does not.</p>
<p style="margin-top: 10px; font-size: 13px; line-height: 1.5; color: #5F6773">Illustrative market inputs: gold at the price set above, moving about {pct(d["inputs"]["gold_volatility"])} a year; a risk-free rate of {pct(d["inputs"]["real_rate"])} after inflation; building starts in {WORDS.get(years_to_start, str(years_to_start))} year{"" if years_to_start == 1 else "s"} and takes {WORDS.get(h["preproduction_years"], str(h["preproduction_years"]))}.</p>
<div style="margin-top: 14px"><p style="font-size: 13px; font-weight: 700; color: #0F2747; margin: 0 0 6px 0">Gold prices used for valuation, not a forecast {tip(f"Forty of the {n_paths:,} paths, built from today's gold price and interest rates, the way options are priced. They are for valuing the mine, not a prediction of where gold will go. The share of lines drawn in gold matches the implied odds above.", "tt-fan")}</p>{fan_chart(d, odds0)}</div>
<div class="pi-stats"><div><b data-k="g50">{usd(g0["median"])}</b><span>middle path after 12 years</span></div><div><b data-k="g90">{usd(g0["p5"])} to {usd(g0["p95"])}</b><span>where 9 in 10 paths end</span></div></div>
<p style="margin-top: 22px; font-size: 13px; font-weight: 700; color: #0F2747">Build cost in each outcome, against the estimate in the study {tip(f"Drawn from the record of past mines (Bertisen and Davis, 2008). In the engine's draws the build costs {ov['mean_pct']}% more than planned on average, and about {ov['double_or_more_in_100']} in 100 cost double or more.", "tt-oh")}</p>
{overrun_chart(d)}
</div>

<div class="pi-card">
<div class="pi-k"><span aria-hidden="true">3</span><h3>Work out what it is worth if built</h3></div>
<p>The same simulated outcomes give the value to this buyer. It differs from the study value for three reasons, each one measured.</p>
<div class="pi-bars">
<div class="pi-bar"><span>Study value</span><div class="t"><div class="f" style="width: {h["npv_after_tax_usd_m"] / bar_scale * 100:.1f}%; background: #8A96A8"></div><span class="v" style="left: {h["npv_after_tax_usd_m"] / bar_scale * 100:.1f}%">{usd_m(h["npv_after_tax_usd_m"])}</span></div></div>
<div class="pi-bar"><span>Worth if built</span><div class="t"><div class="f" style="width: calc(var(--vw) * 100%); background: #0F2747"></div><span class="v" data-k="value" style="left: calc(var(--vw) * 100%)">{usd_m(v0)}</span></div></div>
<div class="pi-bar"><span>Price paid</span><div class="t"><div class="f" style="width: calc(var(--pw) * 100%); background: #B8862B"></div><span class="v" data-k="price" style="left: calc(var(--pw) * 100%)">{usd_m(p0)}</span></div></div>
</div>
<p style="margin-top: 18px; font-size: 13px; font-weight: 700; color: #0F2747">From the study value to worth if built, at the starting settings (US$M)</p>
<div class="pi-brg"><div><span>Study value</span><b>{bs["study"]}</b></div><div><span>Gold at today's price, today's interest rates, {WORDS.get(years_to_start, str(years_to_start))} year{"" if years_to_start == 1 else "s"} to start</span><b>{signed(bs["market"])}</b></div><div><span>Cost overruns, as in past mines</span><b>{signed(bs["overruns"])}</b></div><div><span>The {ret0} extra return the buyer needs</span><b>{signed(bs["return"])}</b></div><div><span>Worth if built</span><b>{bs["worth_if_built"]}</b></div></div>
<p style="margin-top: 10px; font-size: 13px; line-height: 1.5; color: #5F6773">The steps are applied in this order, and their sizes depend on the order. The first assumes gold is expected to rise with interest rates, with nothing earned from holding it.</p>
</div>

<div class="pi-card">
<div class="pi-k"><span aria-hidden="true">4</span><h3>Solve for the one thing nobody states</h3></div>
<p>A price reflects two things: the extra return the buyer needs and the chance the mine gets built. If it is never built the buyer gets nothing. So once the return is stated, the price gives the chance.</p>
<div class="pi-step4"><div class="pi-ok"><div class="pi-eqn"><span data-k="price">{usd_m(p0)}</span><i>÷</i><span data-k="value">{usd_m(v0)}</span><i>=</i><span class="res" data-k="odds">{odds0}%</span></div></div>
<div class="pi-ns"><div class="pi-eqn" style="font-size: 22px">The price is above worth if built. No odds are high enough.</div></div></div>
<div class="pi-ob" aria-hidden="true"><div class="pi-obt"><div class="pi-obf"></div><div class="pi-obm"><span>price paid</span></div></div><div class="pi-obe"><span>US$0 if never built</span><span>worth if built</span></div></div>
<p style="margin-top: 16px; font-size: 14px; color: #5F6773">This reading assumes the mine is built on schedule. A different build date changes the odds; the deal pages show by how much.</p>
<div class="pi-says"><div><b>What it says</b><span>What a price implies about the chance of a build, once the buyer's return is stated.</span></div><div><b>What it depends on</b><span>The return, the gold price and the costs set above. Change one and the answer moves.</span></div><div><b>What it does not say</b><span>That a price is too high or too low, or what will happen to the mine.</span></div></div>
</div>

</div>
</section>

<section class="pi-wrap pi-sec">
<div class="pi-card pi-torcard">
<h2 class="pi-h2">What moves the answer</h2>
<p class="pi-sub">A guess gives one number. The engine shows what the number depends on, and by how much.</p>
<span class="pi-fix">Fixed at the starting settings: {usd_m(p0)} paid, {ret0} extra return, gold {usd(dflt["gold"])}. The answer there is {sens["base"]}%. Each bar changes one thing.</span>
<div class="pi-tor">{sensitivity_rows(d)}</div>
<p style="margin: 16px 0 0 0; font-size: 14px; line-height: 1.55; color: #5F6773; max-width: 860px">The dark line marks {sens["base"]}%. A wide bar means the answer leans on that assumption, so results are always shown with their assumptions. How much gold swings hardly matters for a whole mine, because gains and losses roughly cancel; it matters for shareholders and for when to build.</p>
</div>
</section>

<section id="deals" class="pi-wrap pi-sec">
<div class="pi-band">
{contours(1200, 300, 900, 60, "#5B7BAA", 0.5, n=8, step=50)}
{survey(1200, 300, "#7C9BC9", 0.28, 5, holes=5, grid=150)}
<div><h2>It has been run on real prices</h2><p>Two royalty purchases and two takeovers of real projects, each with its sources. A test on 85 projects of whether these odds tell you which mines get built is under way.</p></div>
<p style="display: flex; flex-wrap: wrap; gap: 12px; margin: 0; position: relative"><a class="pi-btn" href="{LINKS["deals"]}">See the real deals</a></p>
</div>
</section>

<footer class="pi-wrap pi-foot">
<p style="margin: 0; max-width: 640px">Built by <a href="{LINKS["credit"]}" target="_blank" rel="noopener" style="font-weight: 600">Muhammad Mujtaba Moeen</a>. Nothing here is investment advice.</p>
<p style="margin: 0; display: flex; gap: 28px"><a href="{LINKS["read"]}" style="font-weight: 600; padding: 12px 0">How to read this site</a><a href="{LINKS["code"]}" style="font-weight: 600; padding: 12px 0">Code and sources</a></p>
</footer>
</div>
</div>
</div>
<script type="application/json" id="pi-data">{data_json}</script>
<script src="assets/home.js" defer></script>
</body>
</html>
"""


def build(data_path: Path, out: Path) -> Path:
    """Write the site to ``out`` and return the page path."""
    d = json.loads(data_path.read_text(encoding="utf-8"))
    page = build_page(d)
    if "—" in page:
        raise ValueError("the page contains an em dash")
    if out.exists():
        shutil.rmtree(out)
    (out / "assets" / "fonts").mkdir(parents=True)
    (out / "index.html").write_text(page, encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    shutil.copy(SITE / "src" / "home.js", out / "assets" / "home.js")
    for f in (SITE / "assets" / "fonts").iterdir():
        shutil.copy(f, out / "assets" / "fonts" / f.name)
    shutil.copy(data_path, out / "example.json")
    return out / "index.html"


def main() -> None:
    """Build the site."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", type=Path, default=SITE / "data" / "example.json")
    parser.add_argument("--out", type=Path, default=SITE / "_site")
    args = parser.parse_args()
    print(f"wrote {build(args.data, args.out)}")


if __name__ == "__main__":
    main()
