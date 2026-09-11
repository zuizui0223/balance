#!/usr/bin/env python3
"""Assemble the canonical BALANCE manuscript from frozen section sources."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "manuscript" / "BALANCE_MANUSCRIPT_V1.md"

TITLE = "Why conflict persists: a theory and evidence synthesis of the sandwiched regime between integration and differentiation"

SECTIONS = [
    ("Abstract", ROOT / "docs" / "BALANCE_ABSTRACT_V1.md"),
    ("Introduction", ROOT / "docs" / "BALANCE_INTRODUCTION_MANUSCRIPT_TEXT_V1.md"),
    ("Theory", ROOT / "docs" / "BALANCE_THEORY_MANUSCRIPT_TEXT_V1.md"),
    ("Empirical synthesis methods", ROOT / "docs" / "BALANCE_EMPIRICAL_METHODS_MANUSCRIPT_TEXT_V1.md"),
    ("Results", ROOT / "docs" / "BALANCE_RESULTS_MANUSCRIPT_TEXT_V1.md"),
    ("Discussion", ROOT / "docs" / "BALANCE_DISCUSSION_SPINE_V1.md"),
]

CAPTIONS = [
    ("Figure 1", ROOT / "docs" / "BALANCE_FIGURE1_CAPTION_V1.md"),
    ("Figure 2", ROOT / "docs" / "BALANCE_FIGURE2_CAPTION_V1.md"),
    ("Figure 3", ROOT / "docs" / "BALANCE_FIGURE3_CAPTION_V1.md"),
]


def _strip_source_heading(text: str) -> str:
    lines = text.strip().splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
    return "\n".join(lines).strip()


def build_manuscript() -> str:
    parts = [f"# {TITLE}", "", "## Manuscript status", "", "Theory + literature-pattern synthesis draft. Direct focal worldline validation is intentionally retained as the final unresolved empirical layer, not as prerequisite evidence for the manuscript's general claims."]
    for heading, path in SECTIONS:
        if not path.exists():
            raise FileNotFoundError(path)
        body = _strip_source_heading(path.read_text(encoding="utf-8"))
        parts.extend(["", f"## {heading}", "", body])
    parts.extend([
        "",
        "## Figure set",
        "",
        "- Figure 1: `figures/BALANCE_FIGURE1_THEORY_EMPIRICAL_SPINE_V1.svg` — theory-to-empirics spine.",
        "- Figure 2: `figures/BALANCE_FIGURE2_Q1B_QUANTITATIVE_V1.svg` — strict Q1B quantitative synthesis and specificity controls.",
        "- Figure 3: `figures/BALANCE_FIGURE3_REALITY_PATTERN_MAP_V1.svg` — source-adjudicated recurrence map by pattern class and biological domain.",
        "",
        "## Figure captions",
    ])
    for heading, path in CAPTIONS:
        if not path.exists():
            raise FileNotFoundError(path)
        body = _strip_source_heading(path.read_text(encoding="utf-8"))
        parts.extend(["", f"### {heading}", "", body])
    parts.extend([
        "",
        "## Current citation status",
        "",
        "Primary-source identities and DOIs are frozen in `data/BALANCE_MANUSCRIPT_CITATION_LEDGER_V1.csv`; all 17 Figure 3 clusters are mapped to manuscript citation keys in `data/BALANCE_PATTERN_CLUSTER_CITATION_MAP_V1.csv`. Formal in-text citation formatting and the final Literature Cited section remain a manuscript-production task; no uncited general claim should be promoted beyond the source-adjudicated claim ceilings recorded in the repository.",
    ])
    return "\n".join(parts).rstrip() + "\n"


def main(out_path: str | None = None) -> None:
    out = Path(out_path) if out_path else DEFAULT_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_manuscript(), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)
