#!/usr/bin/env python3
"""Build the BALANCE theory-to-empirics flagship SVG from frozen evidence ledgers."""
from __future__ import annotations

import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERN = ROOT / "data" / "BALANCE_PATTERN_READOUT_V1.json"
BOUNDARY = ROOT / "data" / "BALANCE_REALITY_BOUNDARY_READOUT_V1.csv"
POOL = ROOT / "data" / "BALANCE_Q1B_FIRST_POOL_V1.json"
LAYER_MAP = ROOT / "data" / "BALANCE_THEORY_EMPIRICAL_LAYER_MAP_V1.csv"
DEFAULT_OUT = ROOT / "figures" / "BALANCE_FIGURE1_THEORY_EMPIRICAL_SPINE_V1.svg"


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _load() -> dict:
    pattern = json.loads(PATTERN.read_text(encoding="utf-8"))
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    with BOUNDARY.open(encoding="utf-8", newline="") as handle:
        boundary = list(csv.DictReader(handle))
    with LAYER_MAP.open(encoding="utf-8", newline="") as handle:
        layer_map = list(csv.DictReader(handle))

    counts = {}
    for row in boundary:
        counts[row["layer"]] = counts.get(row["layer"], 0) + 1

    direct = next(row for row in layer_map if row["theory_object"] == "shared_vs_differentiated_worldline")
    return {
        "pattern": pattern,
        "pool": pool,
        "boundary_counts": counts,
        "direct_status": direct["status"],
        "direct_evidence": direct["current_evidence"],
    }


def _box(x: int, y: int, w: int, h: int, title: str, lines: list[str], klass: str) -> str:
    body = [
        f'<rect class="{klass}" x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/>',
        f'<text class="box-title" x="{x + 18}" y="{y + 30}">{_esc(title)}</text>',
    ]
    yy = y + 58
    for line in lines:
        body.append(f'<text class="box-text" x="{x + 18}" y="{yy}">{_esc(line)}</text>')
        yy += 23
    return "\n".join(body)


def build_svg() -> str:
    d = _load()
    p = d["pattern"]
    c = d["boundary_counts"]
    pool = d["pool"]
    strict = c.get("STRICT_POSITIVE", 0)
    negative = c.get("NEGATIVE_CONTROL", 0)
    boundary = c.get("BOUNDARY", 0)
    attribution = c.get("ATTRIBUTION_FAIL", 0)

    width, height = 1500, 850
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
  .bg {{ fill: #ffffff; }}
  .theory {{ fill: #f2f2f2; stroke: #222; stroke-width: 2; }}
  .empirical {{ fill: #ffffff; stroke: #222; stroke-width: 2; }}
  .boundary {{ fill: #fafafa; stroke: #666; stroke-width: 1.5; stroke-dasharray: 6 5; }}
  .gap {{ fill: #ffffff; stroke: #111; stroke-width: 2.5; stroke-dasharray: 10 6; }}
  .title {{ font: 700 27px sans-serif; fill: #111; }}
  .lane-title {{ font: 700 18px sans-serif; fill: #333; letter-spacing: 1px; }}
  .box-title {{ font: 700 18px sans-serif; fill: #111; }}
  .box-text {{ font: 15px sans-serif; fill: #222; }}
  .small {{ font: 13px sans-serif; fill: #444; }}
  .arrow {{ stroke: #222; stroke-width: 2.5; fill: none; marker-end: url(#arrow); }}
  .thin-arrow {{ stroke: #666; stroke-width: 1.5; fill: none; marker-end: url(#arrowSmall); }}
</style>
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#222"/></marker>
  <marker id="arrowSmall" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#666"/></marker>
</defs>
<rect class="bg" x="0" y="0" width="1500" height="850"/>
<text class="title" x="60" y="52">BALANCE: theory → reality-pattern recovery → remaining identification gap</text>
<text class="lane-title" x="60" y="105">THEORY</text>
<text class="lane-title" x="60" y="405">EMPIRICAL RECOVERY</text>''']

    parts.append(_box(160, 125, 335, 175, "1  Conflict active", ["Shared coordinate serves ≥2 functions", "Opposing demands create L > 0", "Conflict is prerequisite, not BALANCE itself"], "theory"))
    parts.append(_box(590, 125, 335, 175, "2  Sandwiched regime", ["Conflict remains active", "Shared / integrated state persists", "ρ = W*S − W*D > 0 defines occupancy"], "theory"))
    parts.append(_box(1020, 125, 335, 175, "3  Boundary / differentiation", ["Context shifts relative worldlines", "ρ approaches or crosses 0", "Differentiation becomes favoured"], "theory"))
    parts.append('<path class="arrow" d="M495 212 L575 212"/>')
    parts.append('<path class="arrow" d="M925 212 L1005 212"/>')

    parts.append(_box(160, 435, 335, 205, "R1  Q1B conflict layer", [f"strict positives = {strict}", f"design-matched negatives = {negative}", "first random-effects pool completed", "all 95% CIs include 0 at k=3"], "empirical"))
    parts.append(_box(590, 435, 335, 205, "R2–R3  Persistence geometry", [f"pattern-ledger clusters = {p['n_independent_clusters']}", f"middle-regime signatures = {p['n_middle_regime_signature_clusters']}", f"conflict-without-splitting = {p['n_conflict_without_splitting_clusters']}", f"boundary-crossing clusters = {p['n_boundary_crossing_clusters']}"], "empirical"))
    parts.append(_box(1020, 435, 335, 205, "R4  Direct worldline reserve", [d["direct_evidence"].replace("_", " "), f"status = {d['direct_status']}", "W*S, W*D, ρ, Φ, ξ, dB not identified", "final-stage empirical target"], "gap"))
    parts.append('<path class="arrow" d="M495 537 L575 537"/>')
    parts.append('<path class="arrow" d="M925 537 L1005 537"/>')

    parts.append('<path class="thin-arrow" d="M327 300 L327 420"/>')
    parts.append('<path class="thin-arrow" d="M757 300 L757 420"/>')
    parts.append('<path class="thin-arrow" d="M1187 300 L1187 420"/>')

    parts.append(_box(160, 690, 765, 105, "Application boundaries retained outside strict Q1B", [f"estimand boundaries = {boundary}  |  attribution failures = {attribution}", "Sequential-filter, discrete-morph, and attribution-failure cases constrain applicability rather than inflate k."], "boundary"))
    parts.append(_box(1020, 690, 335, 105, "Claim ceiling", ["Pattern recurrence ≠ natural prevalence", "Q1B / ledger ≠ direct BALANCE occupancy"], "boundary"))

    parts.append(f'<text class="small" x="60" y="830">Frozen first pool: k={pool["independent_clusters"]}; moderator meta-regression prohibited until k≥5 with ≥2 clusters per represented level.</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main(out_path: str | None = None) -> None:
    out = Path(out_path) if out_path else DEFAULT_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_svg(), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)
