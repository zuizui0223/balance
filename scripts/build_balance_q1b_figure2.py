#!/usr/bin/env python3
"""Build Figure 2: positive-admitted Q1B study points, conditional summaries, and specificity controls."""
from __future__ import annotations

import csv
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POINTS = ROOT / "data" / "BALANCE_Q1B_FIGURE2_POINTS_V1.csv"
ADJACENT = ROOT / "data" / "BALANCE_ADJACENT_QUANTITATIVE_LANES_V1.csv"
DEFAULT_OUT = ROOT / "figures" / "BALANCE_FIGURE2_Q1B_QUANTITATIVE_V1.svg"

CONTRASTS = [
    ("pollinator_given_antagonist_present", "Pollinator | antagonist present"),
    ("pollinator_given_antagonist_absent", "Pollinator | antagonist absent"),
    ("antagonist_given_open_pollination", "Antagonist | open pollination"),
    ("antagonist_given_supplemented_pollination", "Antagonist | supplemented pollination"),
]
STUDY_ORDER = ["Fragaria", "Impatiens", "Gymnadenia", "Q1B pooled"]
XMIN, XMAX = -1.2, 1.2


def _esc(x: object) -> str:
    return html.escape(str(x), quote=True)


def _x(v: float, left: float, width: float) -> float:
    return left + (v - XMIN) / (XMAX - XMIN) * width


def _load_points():
    with POINTS.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    by = {}
    for r in rows:
        by[(r["contrast"], r["cluster"])] = r
    return by


def _negative_summary():
    with ADJACENT.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    neg = [r for r in rows if r["pooling_eligibility"] == "NEGATIVE_CONTROL_ONLY"]
    return neg


def build_svg() -> str:
    data = _load_points()
    negatives = _negative_summary()
    width, height = 1480, 760
    plot_w = 250
    panel_x = [70, 420, 770, 1120]
    row_y = {"Fragaria": 205, "Impatiens": 255, "Gymnadenia": 305, "Q1B pooled": 375}
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
.bg {{ fill:#fff; }}
.title {{ font:700 25px sans-serif; fill:#111; }}
.panel-title {{ font:700 15px sans-serif; fill:#111; }}
.axis {{ stroke:#333; stroke-width:1.2; }}
.zero {{ stroke:#777; stroke-width:1; stroke-dasharray:4 4; }}
.point {{ fill:#111; }}
.pool {{ fill:#fff; stroke:#111; stroke-width:2; }}
.ci {{ stroke:#111; stroke-width:2.2; }}
.label {{ font:13px sans-serif; fill:#222; }}
.small {{ font:12px sans-serif; fill:#444; }}
.note-box {{ fill:#fafafa; stroke:#666; stroke-width:1.4; stroke-dasharray:6 5; }}
</style>
<rect class="bg" x="0" y="0" width="{width}" height="{height}"/>
<text class="title" x="55" y="45">BALANCE Q1B: conditional summary of three positive-admitted clusters</text>
<text class="small" x="55" y="72">Admission required the registered positive conflict pattern; diamonds summarize admitted positives and are not a general-effect meta-analysis. Negative controls remain outside the numerator.</text>''']

    for idx, (key, label) in enumerate(CONTRASTS):
        x0 = panel_x[idx]
        plot_left = x0 + 20
        parts.append(f'<text class="panel-title" x="{x0}" y="118">{_esc(label)}</text>')
        y_axis = 425
        parts.append(f'<line class="axis" x1="{plot_left}" y1="{y_axis}" x2="{plot_left+plot_w}" y2="{y_axis}"/>')
        zx = _x(0, plot_left, plot_w)
        parts.append(f'<line class="zero" x1="{zx}" y1="145" x2="{zx}" y2="{y_axis}"/>')
        for tick in [-1.0, -0.5, 0, 0.5, 1.0]:
            tx = _x(tick, plot_left, plot_w)
            parts.append(f'<line class="axis" x1="{tx}" y1="{y_axis}" x2="{tx}" y2="{y_axis+5}"/>')
            parts.append(f'<text class="small" x="{tx-10}" y="{y_axis+22}">{tick:g}</text>')

        for cluster in STUDY_ORDER:
            r = data[(key, cluster)]
            est = float(r["estimate"])
            px = _x(est, plot_left, plot_w)
            py = row_y[cluster]
            if cluster == "Q1B pooled":
                lo, hi = float(r["ci_low"]), float(r["ci_high"])
                lx, hx = _x(lo, plot_left, plot_w), _x(hi, plot_left, plot_w)
                parts.append(f'<line class="ci" x1="{lx}" y1="{py}" x2="{hx}" y2="{py}"/>')
                parts.append(f'<polygon class="pool" points="{px-7},{py} {px},{py-7} {px+7},{py} {px},{py+7}"/>')
            else:
                parts.append(f'<circle class="point" cx="{px}" cy="{py}" r="5"/>')
            if idx == 0:
                display = "conditional summary" if cluster == "Q1B pooled" else cluster
                parts.append(f'<text class="label" x="{x0-5}" y="{py+5}" text-anchor="end">{_esc(display)}</text>')

    parts.append('<rect class="note-box" x="55" y="500" width="1370" height="190" rx="14"/>')
    parts.append('<text class="panel-title" x="78" y="532">Specificity controls kept outside the strict positive-admitted Q1B summary</text>')
    y = 562
    for r in negatives:
        parts.append(f'<text class="label" x="85" y="{y}">{_esc(r["system_taxon"])} — {_esc(r["effect_status"])}: {_esc(r["point_estimates"])}</text>')
        y += 34
    parts.append('<text class="small" x="85" y="650">Boundary lanes (Ipomopsis sequential filter; Primula discrete morph) and the Gymnadenia 2019 attribution failure are reported in Figure 1 / the reality-boundary readout, not summarized here.</text>')
    parts.append('<text class="small" x="55" y="735">Claim ceiling: conditional positive-case Q1B summary only; k=3 does not estimate a design-wide mean or identify direct BALANCE occupancy, W*S, W*D, ρ, Φ, ξ, or dB.</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main(out_path: str | None = None):
    out = Path(out_path) if out_path else DEFAULT_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_svg(), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)
