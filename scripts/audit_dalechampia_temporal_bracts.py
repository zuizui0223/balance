#!/usr/bin/env python3
"""Read-only Dalechampia reported source anchors -> qualified staged readout."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from balance_domain.dalechampia_temporal import audit_dalechampia_temporal_bracts


def build_readout(source_file: Path, output_file: Path) -> dict:
    if output_file.exists():
        raise ValueError("Dalechampia reported-source output already exists")
    raw = source_file.read_bytes()
    source = json.loads(raw)
    out = audit_dalechampia_temporal_bracts(source)
    out["source_json_sha256"] = hashlib.sha256(raw).hexdigest()
    out["source_semantics"] = (
        "published reported contrasts, not independent raw reanalysis; "
        "2012 and 2013 studies are separate contexts from 2015"
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", prefix=".dalechampia-temporal-",
        suffix=".tmp", dir=output_file.parent, delete=False
    ) as f:
        tmp = Path(f.name)
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    try:
        os.replace(tmp, output_file)
    finally:
        if tmp.exists():
            tmp.unlink()
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source", type=Path,
        default=ROOT / "data/DALECHAMPIA_TEMPORAL_BRACT_SOURCE_V1.json",
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    readout = build_readout(args.source, args.out)
    print(json.dumps({
        "status": readout["status"],
        "2015_seed_mass_contrasts": len(readout["postanthesis_2015"]["contrasts"]),
        "structural_S_D_worldlines_identified": readout["structural_S_D_worldlines_identified"],
        "direct_BALANCE_occupancy_identified": readout["direct_BALANCE_occupancy_identified"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
