#!/usr/bin/env python3
"""Build Figure 3: source-adjudicated BALANCE pattern-class × domain recurrence map."""
from __future__ import annotations

import csv
import html
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "BALANCE_PATTERN_LEDGER_V1.csv"
DEFAULT_OUT = ROOT / "figures" / "BALANCE_FIGURE3_REALITY_PATTERN_MAP_V1.svg"

PATTERN_ORDER = [
    "CONFLICT_WITHOUT_SPLITTING",
    "PERSISTENT_INTEGRATION_WITH_ALTERNATIVE_AVAILABLE",
    "SANDWICHED_TRANSITION_MOSAIC",
    "BOUNDARY_CROSSING",
    "DIRECT_DIFFERENTIATION",
    "UNRESOLVED",
]
DOMAIN_ORDER = [
    "plant",
    "protein_function",
    "gene_regulatory_architecture",
    "genome_architecture_ecological_strategy",
    "vertebrate_morphology",
]
MIDDLE = {
    "CONFLICT_WITHOUT_SPLITTING",
    "PERSISTENT_INTEGRATION_WITH_ALTERNATIVE_AVAILABLE",
    "SANDWICHED_TRANSITION_MOSAIC",
}


def _esc(v: object) -> str:
    return html.escape(str(v), quote=True)


def _load():
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    clusters = {(r["cluster_id"], r["domain"], r["pattern_class"]) for r in rows}
    counts = Counter((domain, pattern) for _, domain, pattern in clusters)
    return rows, clusters, counts


def build_svg() -> str:
    rows, clusters, counts = _load()
    n = len({c for c, _, _ in clusters})
    middle_n = len({c for c, _, p in clusters if p in MIDDLE})
    unresolved_n = len({c for c, _, p in clusters if p == "UNRESOLVED"})
    boundary_n = len({c for c, _, p in clusters if p == "BOUNDARY_CROSSING"})

    width, height = 1500, 860
    left, top = 410, 150
    col_w, row_h = 190, 88
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
.bg {{ fill:#fff; }}
.title {{ font:700 25px sans-serif; fill:#111; }}
.subtitle {{ font:14px sans-serif; fill:#444; }}
.header {{ font:700 13px sans-serif; fill:#222; }}
.rowlabel {{ font:13px sans-serif; fill:#222; }}
.grid {{ stroke:#ddd; stroke-width:1; }}
.middle {{ fill:#222; stroke:#111; stroke-width:1.2; }}
.other {{ fill:#fff; stroke:#333; stroke-width:1.5; }}
.unresolved {{ fill:#fff; stroke:#777; stroke-width:1.5; stroke-dasharray:4 3; }}
.count {{ font:700 12px sans-serif; fill:#fff; text-anchor:middle; dominant-baseline:middle; }}
.count-dark {{ font:700 12px sans-serif; fill:#222; text-anchor:middle; dominant-baseline:middle; }}
.note {{ font:13px sans-serif; fill:#333; }}
.box {{ fill:#fafafa; stroke:#666; stroke-width:1.3; stroke-dasharray:6 5; }}
</style>
<rect class="bg" x="0" y="0" width="{width}" height="{height}"/>
<text class="title" x="55" y="48">BALANCE reality-pattern map: recurrence across pattern classes and biological domains</text>
<text class="subtitle" x="55" y="76">Circle size encodes independent-cluster count within the screened, source-adjudicated ledger. This is a recurrence map, not an estimate of natural prevalence.</text>''']

    labels = {
        "plant": "Plant",
        "protein_function": "Protein function",
        "gene_regulatory_architecture": "Gene-regulatory",
        "genome_architecture_ecological_strategy": "Genome / ecological",
        "vertebrate_morphology": "Vertebrate morphology",
    }
    rowlabels = {
        "CONFLICT_WITHOUT_SPLITTING": "Conflict without splitting",
        "PERSISTENT_INTEGRATION_WITH_ALTERNATIVE_AVAILABLE": "Persistent integration + alternative",
        "SANDWICHED_TRANSITION_MOSAIC": "Sandwiched transition mosaic",
        "BOUNDARY_CROSSING": "Boundary crossing",
        "DIRECT_DIFFERENTIATION": "Direct differentiation",
        "UNRESOLVED": "Unresolved",
    }

    for j, domain in enumerate(DOMAIN_ORDER):
        x = left + j * col_w + col_w / 2
        parts.append(f'<text class="header" x="{x}" y="120" text-anchor="middle">{_esc(labels[domain])}</text>')

    for i, pattern in enumerate(PATTERN_ORDER):
        y = top + i * row_h + row_h / 2
        parts.append(f'<text class="rowlabel" x="{left-22}" y="{y+4}" text-anchor="end">{_esc(rowlabels[pattern])}</text>')
        for j, domain in enumerate(DOMAIN_ORDER):
            x0 = left + j * col_w
            y0 = top + i * row_h
            parts.append(f'<rect class="grid" x="{x0}" y="{y0}" width="{col_w}" height="{row_h}" fill="none"/>')
            c = counts[(domain, pattern)]
            if not c:
                continue
            cx, cy = x0 + col_w/2, y0 + row_h/2
            r = 10 + 6 * (c ** 0.5)
            klass = "middle" if pattern in MIDDLE else ("unresolved" if pattern == "UNRESOLVED" else "other")
            text_class = "count" if klass == "middle" else "count-dark"
            parts.append(f'<circle class="{klass}" cx="{cx}" cy="{cy}" r="{r}"/>')
            parts.append(f'<text class="{text_class}" x="{cx}" y="{cy}">{c}</text>')

    parts.append('<rect class="box" x="55" y="705" width="1370" height="105" rx="14"/>')
    parts.append(f'<text class="header" x="78" y="735">Ledger summary: {n} independent clusters; {middle_n} middle-regime signatures; {boundary_n} boundary-crossing clusters; {unresolved_n} unresolved.</text>')
    parts.append('<text class="note" x="78" y="765">Middle-regime signatures are conflict-without-splitting, persistent integration with an available alternative, and sandwiched transition mosaics.</text>')
    parts.append('<text class="note" x="78" y="792">Counts show recurrence within the adjudicated evidence universe only; they do not estimate natural prevalence or direct BALANCE occupancy.</text>')
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
