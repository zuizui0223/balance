"""Recover the published 2016 Diascia ITS consensus-tree figure.

The source figure is public on the ResearchGate figure page. The downloaded
PNG uses transparency, which can make black taxon labels disappear against a
dark renderer. This utility composites it onto a white background and stores
a SHA256 receipt for visual topology adjudication.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import urllib.request
from pathlib import Path

FIGURE_URL = (
    "https://www.researchgate.net/publication/303275615/figure/download/fig1/"
    "AS%3A362622680616960%401463467392402/"
    "Strict-consensus-tree-of-20-834-EMP-trees-of-the-ITS-region-for-selected-"
    "Diascia-species.png"
)
USER_AGENT = "Mozilla/5.0 BALANCE-Diascia-figure-audit/1.0"


def flatten_png_on_white(data: bytes) -> bytes:
    from PIL import Image

    image = Image.open(io.BytesIO(data)).convert("RGBA")
    white = Image.new("RGBA", image.size, (255, 255, 255, 255))
    white.alpha_composite(image)
    out = io.BytesIO()
    white.convert("RGB").save(out, format="PNG")
    return out.getvalue()


def fetch_figure() -> tuple[bytes, str]:
    request = urllib.request.Request(
        FIGURE_URL,
        headers={"User-Agent": USER_AGENT, "Accept": "image/png,image/*;q=0.9,*/*;q=0.5"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
        data = response.read()
        content_type = response.headers.get("Content-Type", "")
    if "image" not in content_type.casefold() or len(data) < 10_000:
        raise ValueError(
            f"ResearchGate figure response is not a usable image: "
            f"{content_type!r}, {len(data)} bytes"
        )
    return data, content_type


def run(output: Path, workdir: Path) -> dict:
    workdir.mkdir(parents=True, exist_ok=True)
    raw, content_type = fetch_figure()
    flattened = flatten_png_on_white(raw)
    raw_path = workdir / "diascia_its_tree_original.png"
    white_path = workdir / "diascia_its_tree_white.png"
    raw_path.write_bytes(raw)
    white_path.write_bytes(flattened)
    receipt = {
        "analysis": "balance_u3_diascia_2016_tree_figure_recovery_v1",
        "source_url": FIGURE_URL,
        "source_publication": (
            "Hattingh et al. 2016 A forgotten biodiversity hotspot: "
            "Using Diascia to understand drivers of diversification in the "
            "Drakensberg Alpine Centre"
        ),
        "content_type": content_type,
        "raw_size_bytes": len(raw),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "white_background_size_bytes": len(flattened),
        "white_background_sha256": hashlib.sha256(flattened).hexdigest(),
        "raw_path": str(raw_path),
        "white_background_path": str(white_path),
        "claim_ceiling": (
            "published_ITS_tree_figure_recovery_for_visual_topology_audit_only_"
            "not_new_phylogenetic_inference_not_control_adjudication"
        ),
    }
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output, args.workdir), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
