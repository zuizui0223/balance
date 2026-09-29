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

PREVIEW_BASE = (
    "https://i1.rgstatic.net/publication/"
    "290444306_A_forgotten_biodiversity_hotspot_Using_Diascia_to_understand_"
    "drivers_of_diversification_in_the_Drakensberg_Alpine_Centre/"
    "links/5698f4f108ae6169e5515b3c/"
)
FIGURE_URLS = tuple(
    PREVIEW_BASE + name
    for name in ("largepreview.png", "mediumpreview.png", "smallpreview.png")
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


def fetch_figure() -> tuple[bytes | None, str | None, str | None, list[dict]]:
    receipts = []
    for url in FIGURE_URLS:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "image/png,image/*;q=0.9,*/*;q=0.5",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
                data = response.read()
                content_type = response.headers.get("Content-Type", "")
            usable = "image" in content_type.casefold() and len(data) >= 2_000
            receipts.append(
                {
                    "url": url,
                    "status": "FETCHED",
                    "content_type": content_type,
                    "size_bytes": len(data),
                    "usable": usable,
                }
            )
            if usable:
                return data, content_type, url, receipts
        except Exception as exc:  # pragma: no cover - external network
            receipts.append(
                {"url": url, "status": "FETCH_ERROR", "error": repr(exc)}
            )
    return None, None, None, receipts


def run(output: Path, workdir: Path) -> dict:
    workdir.mkdir(parents=True, exist_ok=True)
    raw, content_type, source_url, fetch_receipts = fetch_figure()
    if raw is None:
        receipt = {
            "analysis": "balance_u3_diascia_2016_tree_figure_recovery_v1",
            "status": "PUBLIC_PREVIEW_FETCH_BLOCKED",
            "source_urls": list(FIGURE_URLS),
            "fetch_receipts": fetch_receipts,
            "claim_ceiling": (
                "published_tree_source_located_but_preview_bytes_unavailable_"
                "not_topology_adjudication"
            ),
        }
        output.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return receipt

    flattened = flatten_png_on_white(raw)
    raw_path = workdir / "diascia_its_tree_original.png"
    white_path = workdir / "diascia_its_tree_white.png"
    raw_path.write_bytes(raw)
    white_path.write_bytes(flattened)

    from PIL import Image
    image = Image.open(io.BytesIO(flattened)).convert("RGB")
    width, height = image.size
    # Poster layout places the tree in the centre-right panel. Retain a
    # deterministic broad crop for visual adjudication without OCR.
    crop = image.crop(
        (
            int(width * 0.45),
            int(height * 0.25),
            width,
            int(height * 0.88),
        )
    )
    crop_path = workdir / "diascia_its_tree_crop.png"
    crop.save(crop_path, format="PNG")

    receipt = {
        "analysis": "balance_u3_diascia_2016_tree_figure_recovery_v1",
        "status": "PUBLIC_PREVIEW_RECOVERED",
        "source_url": source_url,
        "source_urls_attempted": list(FIGURE_URLS),
        "fetch_receipts": fetch_receipts,
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
        "tree_crop_path": str(crop_path),
        "image_width": width,
        "image_height": height,
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
