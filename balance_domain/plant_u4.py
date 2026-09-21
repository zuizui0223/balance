"""Guards for the carnivorous-plant pollinator-prey U4 stress-test series."""
from __future__ import annotations

from pathlib import Path

from .plant_macro import load_plant_macro_ledger


EXPECTED_U4_GROUPS = 10
EXPECTED_POSITIVE = 2


def load_u4_cases(path: Path) -> list[dict[str, str]]:
    rows = load_plant_macro_ledger(path)
    if len(rows) != EXPECTED_U4_GROUPS:
        raise ValueError(f"U4 must contain {EXPECTED_U4_GROUPS} registered species cases")
    if {r["sampling_frame_id"] for r in rows} != {"U4_CARNIVOROUS_PPC_STRESS_TEST_V1"}:
        raise ValueError("U4 rows must use the frozen stress-test frame id")
    if any(r["conflict_family"] != "POLLINATOR_PREY" for r in rows):
        raise ValueError("U4 rows must belong to the pollinator-prey conflict family")
    if any(r["adjudication_status"] != "SCREENED" for r in rows):
        raise ValueError("U4 remains a screened stress-test series")
    if any(r["primary_model_eligible"] != "false" for r in rows):
        raise ValueError("U4 stress-test rows cannot be promoted directly to primary model")
    return rows


def build_u4_readout(path: Path) -> dict:
    rows = load_u4_cases(path)
    positive = [r for r in rows if r["conflict_status"] == "POSITIVE"]
    modes = sorted({r["architecture_mode"] for r in rows})
    return {
        "analysis": "balance_plant_u4_carnivorous_ppc_stress_test",
        "n_species_cases": len(rows),
        "n_positive_conflict": len(positive),
        "positive_taxa": sorted(r["system_taxon"] for r in positive),
        "architecture_modes_present": modes,
        "n_selfing_buffered_cases": sum(
            r["autonomous_selfing"] == "PRESENT" for r in rows
        ),
        "claim_ceiling": (
            "mechanism_stress_test_not_prevalence_not_outcome_blind_"
            "not_primary_model_eligible"
        ),
    }
