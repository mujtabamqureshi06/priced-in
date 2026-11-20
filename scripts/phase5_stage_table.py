"""Phase 5: probability and timing of a construction decision by study stage.

Implements sections 4 to 7 of ``docs/phase5/protocol.md`` on the public files in
``data/phase5``:

    uv run python scripts/phase5_stage_table.py OUTPUT_MD

The script writes the commit it runs from and the run time in UTC before any result.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime
from pathlib import Path

import numpy as np

from pricedin.stage_table import (
    aalen_johansen,
    brier,
    cluster_bootstrap,
    cumulative_incidence,
    fine_gray,
    months_between,
    percentile_interval,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "phase5"
CUTOFF = date(2026, 3, 31)
WINDOW_END = date(2022, 3, 31)
STAGES = ("PEA", "PFS", "FS")
N_BOOT, SEED = 2_000, 20261121
DONLIN = "donlin_gold"
# Alternative reading of Witwatersrand Basin (ADR 0068 item 4): decided at the September
# 2025 placement, the later of the two dates the coders gave.
WWB_ALT = (
    ("witwatersrand_basin", "2025-09-15"),
    ("witwatersrand_basin::Qala Shallows", "2025-09-15"),
)


def d(text: str) -> date:
    """Parse an ISO date."""
    return date.fromisoformat(text)


def read(path: Path) -> list[dict[str, str]]:
    """Read a CSV file into a list of dicts."""
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


@dataclass
class Options:
    """One reading of the data: the main table or a robustness variant."""

    lenient: bool = False
    unresolved: bool = False
    drop_frame_low: bool = False
    drop_label_low: bool = False
    drop_donlin: bool = False
    drop_fulltext: bool = False
    partial_as_none: bool = False
    phase4_rule: bool = False
    start_dating: bool = False
    components: bool = False
    split_groups: frozenset[str] = frozenset()
    drop_projects: frozenset[str] = frozenset()
    alt_decisions: tuple[tuple[str, str], ...] = ()


@dataclass
class Entries:
    """Per-entry arrays used by every estimator."""

    pid: list[str] = field(default_factory=list)
    cluster: list[str] = field(default_factory=list)
    stage: list[str] = field(default_factory=list)
    half: list[str] = field(default_factory=list)
    start: list[date] = field(default_factory=list)
    t_dec: list[float] = field(default_factory=list)
    ev_dec: list[bool] = field(default_factory=list)
    t_tk: list[float] = field(default_factory=list)
    ev_tk: list[bool] = field(default_factory=list)
    t_cens: list[float] = field(default_factory=list)
    dropped_decided: list[str] = field(default_factory=list)

    def arrays(self) -> dict[str, np.ndarray]:
        """Numpy views of the per-entry lists."""
        return {
            "pid": np.array(self.pid),
            "cluster": np.array(self.cluster),
            "stage": np.array(self.stage),
            "half": np.array(self.half),
            "t_dec": np.array(self.t_dec, dtype=float),
            "ev_dec": np.array(self.ev_dec, dtype=bool),
            "t_tk": np.array(self.t_tk, dtype=float),
            "ev_tk": np.array(self.ev_tk, dtype=bool),
            "t_cens": np.array(self.t_cens, dtype=float),
        }


def decision_date(lab: dict[str, str], opt: Options) -> date | None:
    """Decision date of a project under the chosen reading, or None."""
    alt = dict(opt.alt_decisions)
    if lab["project_id"] in alt:
        dd_alt = d(alt[lab["project_id"]])
        return dd_alt if dd_alt <= CUTOFF else None
    if lab["outcome"] != "construction_decision" or not lab["decision_date"]:
        return None
    if opt.partial_as_none and lab["partial_development"] == "yes":
        return None
    if opt.phase4_rule and lab["decision_basis"] == "construction_started_funding_unstated":
        return None
    dd = d(lab["decision_date"])
    if opt.start_dating and lab["construction_start_date"]:
        dd = min(dd, d(lab["construction_start_date"]))
    return dd if dd <= CUTOFF else None


def build(opt: Options) -> Entries:
    """Assemble entries and their outcomes under ``opt``."""
    labels = {r["project_id"]: r for r in read(DATA / "labels.csv")}
    rows = [
        r for r in read(DATA / "frame_entries.csv") if opt.lenient or r["in_lenient_only"] != "True"
    ]
    if opt.unresolved:
        rows += read(DATA / "unresolved_entries.csv")
    comp_outcome: dict[str, dict[str, str]] = {}
    if opt.components or opt.split_groups:
        linked = (
            {r["project_id"] for r in read(DATA / "linked_groups.csv")}
            if opt.components
            else set(opt.split_groups)
        )
        rows = [r for r in rows if r["project_id"] not in linked]
        for c in read(DATA / "components.csv"):
            if not c["stage"] or c["project_id"] not in linked:
                continue
            cid = f"{c['project_id']}::{c['component']}"
            rows.append(
                {
                    "project_id": cid,
                    "stage": c["stage"],
                    "date": c["date"],
                    "half": "estimate" if d(c["date"]).year <= 2016 else "test",
                    "in_lenient_only": "False",
                }
            )
            comp_outcome[cid] = {
                **labels[c["project_id"]],
                "project_id": cid,
                "outcome": c["outcome"],
                "decision_date": c["decision_date"],
                "decision_basis": c["basis"],
                "label_confidence": c["label_confidence"],
                "partial_development": c["partial_development"],
                "construction_start_date": "",  # not coded for components
            }
    e = Entries()
    for r in rows:
        pid = r["project_id"]
        lab = comp_outcome.get(pid) or labels[pid]
        if opt.drop_donlin and pid == DONLIN:
            continue
        if pid.split("::")[0] in opt.drop_projects:
            continue
        if opt.drop_frame_low and lab["frame_low_confidence"] == "True":
            continue
        if opt.drop_label_low and lab["label_confidence"] == "low":
            continue
        if opt.drop_fulltext and lab["discovery_source"] == "fulltext":
            continue
        t0 = d(r["date"])
        end = d(lab["last_info_date"]) if lab["last_info_date"] else CUTOFF
        dd = decision_date(lab, opt)
        if dd is not None and dd < t0:
            e.dropped_decided.append(f"{pid} {r['stage']}")
            continue
        tks = [d(x) for x in lab["takeover_dates"].split(";") if x]
        tks = [x for x in tks if t0 <= x <= end]
        e.pid.append(pid)
        e.cluster.append(pid.split("::")[0])  # components cluster with their group
        e.stage.append(r["stage"])
        e.half.append(r["half"])
        e.start.append(t0)
        e.t_cens.append(months_between(t0, end))
        if dd is not None and dd <= end:
            e.t_dec.append(months_between(t0, dd))
            e.ev_dec.append(True)
        else:
            e.t_dec.append(months_between(t0, end))
            e.ev_dec.append(False)
        if tks:
            e.t_tk.append(months_between(t0, min(tks)))
            e.ev_tk.append(True)
        else:
            e.t_tk.append(months_between(t0, end))
            e.ev_tk.append(False)
    return e


def cif_by_stage(a: dict[str, np.ndarray], idx: np.ndarray, which: str = "dec") -> np.ndarray:
    """Cumulative incidence at each horizon for each stage and pooled (4 x 4)."""
    out = []
    st = a["stage"][idx]
    for s in (*STAGES, "All"):
        m = np.ones(idx.size, bool) if s == "All" else st == s
        out.append(cumulative_incidence(a[f"t_{which}"][idx][m], a[f"ev_{which}"][idx][m]))
    return np.concatenate(out)


def fmt(x: float) -> str:
    """Percentage with no decimals."""
    return "n/a" if np.isnan(x) else f"{100 * x:.0f}%"


def fmt1(x: float) -> str:
    """Percentage with one decimal."""
    return "n/a" if np.isnan(x) else f"{100 * x:.1f}%"


def table(e: Entries, which: str = "dec", n_boot: int = N_BOOT) -> list[str]:
    """Markdown table of cumulative incidence by stage with 95% bootstrap intervals."""
    a = e.arrays()
    idx = np.arange(a["pid"].size)
    point = cif_by_stage(a, idx, which).reshape(4, 4)
    draws = cluster_bootstrap(list(a["cluster"]), lambda i: cif_by_stage(a, i, which), n_boot, SEED)
    lo, hi = percentile_interval(draws)
    lo, hi = lo.reshape(4, 4), hi.reshape(4, 4)
    lines = [
        "| Stage | Entries | Projects | Events | 12 months | 24 months | 36 months | 60 months |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for k, s in enumerate((*STAGES, "All")):
        m = np.ones(idx.size, bool) if s == "All" else a["stage"] == s
        cells = [f"{fmt(point[k, h])} ({fmt(lo[k, h])} to {fmt(hi[k, h])})" for h in range(4)]
        lines.append(
            f"| {s} | {int(m.sum())} | {len(set(a['pid'][m]))} | "
            f"{int(a[f'ev_{which}'][m].sum())} | " + " | ".join(cells) + " |"
        )
    return lines


def short_row(e: Entries) -> list[float]:
    """Point estimates of 36-month incidence by stage and pooled."""
    a = e.arrays()
    return list(cif_by_stage(a, np.arange(a["pid"].size)).reshape(4, 4)[:, 2])


def first_entry_only(e: Entries) -> Entries:
    """Section 4 check: one entry per project, at its first study in the window."""
    first: dict[str, int] = {}
    for i, (p, s) in enumerate(zip(e.pid, e.start, strict=True)):
        if p not in first or s < e.start[first[p]]:
            first[p] = i
    keep = sorted(first.values())
    out = Entries()
    for name in (
        "pid",
        "cluster",
        "stage",
        "half",
        "start",
        "t_dec",
        "ev_dec",
        "t_tk",
        "ev_tk",
        "t_cens",
    ):
        setattr(out, name, [getattr(e, name)[i] for i in keep])
    return out


def progression(e: Entries) -> list[str]:
    """Time from a PEA entry to the project's next later-stage entry, and PFS to FS."""
    nxt = {"PEA": ("PFS", "FS"), "PFS": ("FS",)}
    by_pid: dict[str, list[tuple[str, date]]] = {}
    for p, s, t in zip(e.pid, e.stage, e.start, strict=True):
        by_pid.setdefault(p, []).append((s, t))
    lines = [
        "| From | Entries | Moved | 12 months | 24 months | 36 months |",
        "|---|---|---|---|---|---|",
    ]
    for s0, later in nxt.items():
        tt, ev = [], []
        for p, s, t in zip(e.pid, e.stage, e.start, strict=True):
            if s != s0:
                continue
            nexts = [u for (ss, u) in by_pid[p] if ss in later and u > t]
            if nexts:
                tt.append(months_between(t, min(nexts)))
                ev.append(True)
            else:
                tt.append(months_between(t, WINDOW_END))
                ev.append(False)
        ci = cumulative_incidence(np.array(tt), np.array(ev), (12, 24, 36))
        lines.append(f"| {s0} | {len(tt)} | {sum(ev)} | " + " | ".join(fmt(x) for x in ci) + " |")
    return lines


def competing(e: Entries) -> list[str]:
    """Aalen-Johansen incidence when the first of decision and takeover ends the entry."""
    a = e.arrays()
    t = np.minimum(a["t_dec"], a["t_tk"])
    cause = np.where(
        a["ev_dec"] & (a["t_dec"] <= a["t_tk"]),
        1,
        np.where(a["ev_tk"] & (a["t_tk"] < a["t_dec"]), 2, 0),
    )
    lines = [
        "| Stage | Decision first, 36 m | Takeover first, 36 m "
        "| Decision first, 60 m | Takeover first, 60 m |",
        "|---|---|---|---|---|",
    ]
    for s in (*STAGES, "All"):
        m = np.ones(t.size, bool) if s == "All" else a["stage"] == s
        c1, c2 = aalen_johansen(t[m], cause[m], (36, 60))
        lines.append(f"| {s} | {fmt(c1[0])} | {fmt(c2[0])} | {fmt(c1[1])} | {fmt(c2[1])} |")
    x = np.column_stack([(a["stage"] == "PFS").astype(float), (a["stage"] == "FS").astype(float)])

    def fg(i: np.ndarray) -> np.ndarray:
        return fine_gray(t[i], cause[i], a["t_cens"][i], x[i])

    beta = fg(np.arange(t.size))
    draws = cluster_bootstrap(list(a["cluster"]), fg, 500, SEED)
    lo, hi = percentile_interval(draws)
    lines += [
        "",
        "Fine and Gray subdistribution hazard ratios for a construction decision, takeover as the "
        "competing event (reference PEA; 95% interval from 500 bootstrap draws over projects):",
        "",
        f"- PFS: {np.exp(beta[0]):.2f} ({np.exp(lo[0]):.2f} to {np.exp(hi[0]):.2f})",
        f"- FS: {np.exp(beta[1]):.2f} ({np.exp(lo[1]):.2f} to {np.exp(hi[1]):.2f})",
    ]
    return lines


def stability(e: Entries) -> tuple[list[str], dict[str, object]]:
    """Section 7: results (a), (b) and (c) on the 36-month incidence."""
    a = e.arrays()
    est = np.flatnonzero(a["half"] == "estimate")
    test = np.flatnonzero(a["half"] == "test")

    def rates(idx: np.ndarray) -> np.ndarray:
        """36-month incidence for PEA, PFS, FS and pooled."""
        return cif_by_stage(a, idx).reshape(4, 4)[:, 2]

    def observed36(idx: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        keep = idx[(a["ev_dec"][idx] & (a["t_dec"][idx] <= 36)) | (a["t_dec"][idx] >= 36)]
        y = (a["ev_dec"][keep] & (a["t_dec"][keep] <= 36)).astype(float)
        return keep, y

    def stats(ie: np.ndarray, it: np.ndarray) -> np.ndarray:
        pe, pt = rates(ie), rates(it)
        keep, y = observed36(it)
        st = a["stage"][keep]
        f_stage = np.array([pe[STAGES.index(s)] for s in st])
        f_pool = np.full(keep.size, pe[3])
        diff = brier(y, f_pool) - brier(y, f_stage)
        return np.concatenate([[diff], pt[:3] - pe[:3]])

    point = stats(est, test)
    rng = np.random.default_rng(SEED)

    # Projects are drawn once, with all their entries in both halves, so a project with
    # entries in both halves carries its dependence into the interval.
    clusters = a["cluster"]
    uniq = np.unique(clusters)
    rows_of = {p: np.flatnonzero(clusters == p) for p in uniq}
    is_est = a["half"] == "estimate"

    def joint() -> tuple[np.ndarray, np.ndarray]:
        idx = np.concatenate([rows_of[p] for p in rng.choice(uniq, uniq.size)])
        return idx[is_est[idx]], idx[~is_est[idx]]

    draws = np.array([stats(*joint()) for _ in range(N_BOOT)])
    lo, hi = percentile_interval(draws)
    pt = rates(test)
    pe = rates(est)
    order = bool(pt[0] < pt[1] < pt[2])
    lines = [
        f"(a) Stage adds information. 36-month Brier score on the test half with pooled-rate "
        f"forecasts minus the score with stage-rate forecasts (positive favours stage): "
        f"{point[0]:.4f} (95% interval {lo[0]:.4f} to {hi[0]:.4f}).",
        "",
        f"(b) Order. Test-half 36-month incidence: PEA {fmt(pt[0])}, PFS {fmt(pt[1])}, "
        f"FS {fmt(pt[2])}. PEA below PFS below FS: {'yes' if order else 'no'}.",
        "",
        "(c) Stability, per stage (observed test half minus predicted from the estimate half, "
        "36 months):",
        "",
        "| Stage | Estimate half | Test half | Difference (95% interval) "
        "| Test-half decisions | Reading |",
        "|---|---|---|---|---|---|",
    ]
    readings: dict[str, str] = {}
    for k, s in enumerate(STAGES):
        tm = (a["half"] == "test") & (a["stage"] == s)
        n_ev = int((a["ev_dec"][tm] & (a["t_dec"][tm] <= 36)).sum())
        lo_k, hi_k = lo[k + 1], hi[k + 1]
        if n_ev < 5:
            reading = "descriptive only (fewer than 5 decisions)"
        elif lo_k > 0 or hi_k < 0:
            reading = "different"
        elif (hi_k - lo_k) / 2 <= 0.15:
            reading = "consistent"
        else:
            reading = "too imprecise to judge"
        readings[s] = reading
        lines.append(
            f"| {s} | {fmt1(pe[k])} | {fmt1(pt[k])} | {100 * point[k + 1]:+.1f} points "
            f"({100 * lo_k:+.1f} to {100 * hi_k:+.1f}) | {n_ev} | {reading} |"
        )
    return lines, {"brier_diff": point[0], "order": order, "readings": readings}


def git_head() -> str:
    """Commit the script runs from."""
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT, check=False
    ).stdout.strip()


def main() -> None:
    """Write every Phase 5 table to the path given on the command line."""
    out_path = Path(sys.argv[1])
    out: list[str] = [
        "# Phase 5 stage table: run record",
        "",
        f"Commit {git_head()}, run {datetime.now(UTC).isoformat(timespec='seconds')}.",
        "",
    ]
    primary = Options(components=True)
    link_check = DATA / "link_check.csv"
    failed = (
        frozenset(r["project_id"] for r in read(link_check) if r["verdict"] in ("fail", "partial"))
        if link_check.exists()
        else frozenset()
    )
    main_e = build(primary)
    out += [
        "## Construction decision, primary table (linked components kept separate)",
        "",
        *table(main_e),
        "",
        f"Entries dropped because the decision came before that study: "
        f"{len(main_e.dropped_decided)} ({', '.join(main_e.dropped_decided) or 'none'}).",
        "",
    ]
    linked_e = build(Options())
    out += [
        "## Construction decision, linked table (links as fixed with the frame)",
        "",
        *table(linked_e),
        "",
        f"Entries dropped because the decision came before that study: "
        f"{len(linked_e.dropped_decided)} ({', '.join(linked_e.dropped_decided) or 'none'}).",
        "",
    ]
    if failed:
        out += [
            "## Construction decision, linked table with failed links corrected",
            "",
            f"Groups split: {', '.join(sorted(failed))}.",
            "",
            *table(build(Options(split_groups=failed)), n_boot=1000),
            "",
        ]
    out += ["## Takeover of the owner", "", *table(main_e, "tk"), ""]
    out += ["## Check: one entry per project, at its first study in the window", ""]
    out += [*table(first_entry_only(main_e)), ""]
    out += [
        "## Progression to a later-stage study (linked table, observed to 31 March 2022)",
        "",
        *progression(linked_e),
        "",
    ]
    out += ["## Competing risks: the first event ends the entry", "", *competing(main_e), ""]
    s_lines, s_res = stability(main_e)
    out += ["## Stability test (primary table)", "", *s_lines, ""]
    l_lines, l_res = stability(linked_e)
    out += ["## Stability test (linked table)", "", *l_lines, ""]

    def v(**kw: object) -> Callable[[], Entries]:
        return lambda: build(replace(primary, **kw))  # type: ignore[arg-type]

    variants: list[tuple[str, Callable[[], Entries]]] = [
        ("Primary", lambda: main_e),
        ("Linked table, links as fixed", lambda: linked_e),
        ("Linked table, failed links corrected", lambda: build(Options(split_groups=failed))),
        ("Primary without Bardoc", v(drop_projects=frozenset({"bardoc"}))),
        ("Primary, Witwatersrand Basin decided 2025-09-15", v(alt_decisions=WWB_ALT)),
        (
            "Linked table, Witwatersrand Basin decided 2025-09-15",
            lambda: build(Options(alt_decisions=WWB_ALT)),
        ),
        (
            "Linked table without Bardoc",
            lambda: build(Options(drop_projects=frozenset({"bardoc"}))),
        ),
        ("Lenient entries (unconfirmed studies counted)", v(lenient=True)),
        ("With the 3 unresolved projects", v(unresolved=True)),
        ("Without studies resting on press or third-party copies", v(drop_frame_low=True)),
        ("Without low-confidence labels", v(drop_label_low=True)),
        ("Without Donlin", v(drop_donlin=True)),
        ("Without full-text screen additions", v(drop_fulltext=True)),
        ("Partial developments as no decision", v(partial_as_none=True)),
        ("Phase 4 rule (undisclosed funding is no decision)", v(phase4_rule=True)),
        ("Construction-start dating", v(start_dating=True)),
    ]
    out += [
        "## Robustness: 36-month incidence by stage",
        "",
        "| Reading | PEA | PFS | FS | All | Entries |",
        "|---|---|---|---|---|---|",
    ]
    results: dict[str, list[float]] = {}
    for name, fn in variants:
        ev = fn()
        r = short_row(ev)
        results[name] = r
        out.append(f"| {name} | " + " | ".join(fmt1(x) for x in r) + f" | {len(ev.pid)} |")
    sd = build(replace(primary, start_dating=True))

    def within36(e: Entries) -> dict[tuple[str, str], bool]:
        return {
            (p, s): bool(x and t <= 36)
            for p, s, x, t in zip(e.pid, e.stage, e.ev_dec, e.t_dec, strict=True)
        }

    m36, s36 = within36(main_e), within36(sd)
    changed = sum(1 for k, val in m36.items() if k in s36 and s36[k] != val)
    lost = len([k for k in m36 if k not in s36])
    out += [
        "",
        f"Entries whose 36-month outcome changes under construction-start dating: {changed}; "
        f"entries that drop out because construction started before that study: {lost}.",
        "",
        "## Phase 4 rule table",
        "",
        *table(build(replace(primary, phase4_rule=True)), n_boot=1000),
        "",
    ]
    s_res = {"primary": s_res, "linked": l_res}
    out_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    (out_path.with_suffix(".json")).write_text(
        json.dumps({"robustness_36m": results, "stability": s_res}, indent=1, default=str),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
