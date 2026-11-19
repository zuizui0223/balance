"""Run synthetic pollen opportunity predictions; show source-only external anchor.

The published Polemonium article is NOT used to calibrate any parameter.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from balance_domain.pollen_supply_opportunity import (
    build_synthetic_gate_and_order_scenarios,
    build_closed_stock_parameter_sweep,
)

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = ROOT / "data" / "BALANCE_POLEMONIUM_2021_SOURCE_ONLY_ANCHOR_V1.json"

if __name__ == "__main__":
    source = json.loads(ANCHOR.read_text(encoding="utf-8"))
    if (
        source["schema_version"] != "BALANCE_POLEMONIUM_FOLIOSISSIMUM_SOURCE_ANCHOR_V1"
        or source["status"] != "PUBLICATION_REPORTED_RESULTS_ONLY_NOT_RAW_DATA_REANALYSIS"
        or source["source"]["doi"] != "10.1093/aob/mcab050"
        or source["model_link"]["not_added_to_frozen_U6"] is not True
        or source["model_link"]["direct_architecture_worldline"] is not False
    ):
        raise ValueError("Published source anchor or evidence ceiling changed")
    output = {
        "hypothesis_model": build_synthetic_gate_and_order_scenarios(),
        "model_only_parameter_grid": build_closed_stock_parameter_sweep(),
        "external_source_only_anchor": {
            "doi": source["source"]["doi"],
            "taxon": source["source"]["taxon"],
            "article": source["source"]["article_url"],
            "independent_original_research_programmes": (
                source["source"]["number_of_independent_original_research_programmes"]
            ),
            "source_status": source["status"],
            "source_json_sha256": hashlib.sha256(ANCHOR.read_bytes()).hexdigest(),
        },
        "real_observed_new_effects": 0,
        "source_harmonized_fitness_contrasts": 0,
        "v4_architecture_adjudications": 0,
    }
    print(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False))
