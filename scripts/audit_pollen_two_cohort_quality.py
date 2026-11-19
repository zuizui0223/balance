"""Read-only publisher-summary check + synthetic late-cohort efficacy predictions."""
from __future__ import annotations

import json
from pathlib import Path

from balance_domain.pollen_two_cohort_quality import quality_threshold_sweep

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "BALANCE_POLEMONIUM_2021_PRIMARY_DESIGN_AUDIT_V1.json"

if __name__ == "__main__":
    primary = json.loads(SOURCE.read_text(encoding="utf-8"))
    if (
        primary["schema_version"] != "BALANCE_POLEMONIUM_2021_PRIMARY_DESIGN_AUDIT_V1"
        or primary["status"] != "PUBLISHED_PRIMARY_ARTICLE_TEXT_READ_NOT_RAW_DATA"
        or primary["original_publication"]["doi"] != "10.1093/aob/mcab050"
        or primary["evidence"]["2015"]["source_neighbourhood_count"] != 4
        or primary["evidence"]["2016"]["source_neighbourhood_count"] != 10
        or primary["data_recovery"]["exact_original_data_files_retrieved"] is not False
    ):
        raise ValueError("Original 2021 published-source evidence ceiling altered")
    result = {
        "source_audit": {
            "doi": primary["original_publication"]["doi"],
            "year_specific_design": {
                y: {
                    "neighbourhood_count": primary["evidence"][y]["source_neighbourhood_count"],
                }
                for y in ("2015", "2016")
            },
            "no_original_raw_data_reanalysis": True,
            "no_effective_visitor_capacity_randomization": True,
            "no_source_paternity_fitness": True,
        },
        "synthetic_effectiveness_threshold": quality_threshold_sweep(),
        "field_effects_estimated_from_model": 0,
        "v4_outcomes_used": False,
    }
    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False))
