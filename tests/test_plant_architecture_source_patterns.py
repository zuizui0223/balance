"""Regression guards for already screened real source frames, not V4 outcomes."""
from __future__ import annotations

import shutil
import json
import subprocess
import sys

import pytest

from balance_domain.plant_architecture_source_patterns import (
    PILOT_PATH,
    REPO_ROOT,
    U2_PATH,
    analyze,
)


def test_real_u2_and_pilot_are_kept_separate():
    audit = analyze()
    assert audit["schema"] == "BALANCE_SOURCE_STRATIFIED_TRAIT_ARCHITECTURE_V1"
    assert audit["not_pooled"] is True
    u2, pilot = audit["u2"], audit["plant_pilot"]
    assert (u2["source_rows"], u2["distinct_dependency_groups"]) == (22, 22)
    assert u2["status_counts"] == {
        "NO_DEMONSTRATED_CONFLICT": 14,
        "POSITIVE": 8,
    }
    assert u2["conflict_positive_four_class"] == {
        "MOSAIC": 1,
        "NONSTRUCTURAL_SEPARATION": 3,
        "SHARED": 4,
    }
    assert u2["no_demonstrated_conflict_four_class"] == {
        "MOSAIC": 9,
        "NONSTRUCTURAL_SEPARATION": 2,
        "UNRESOLVED": 3,
    }
    assert u2["conflict_positive_structural_true"] == 0
    assert u2["conflict_positive_structural_unresolved"] == 1
    assert u2["conflict_positive_structural_record_bounds"] == {
        "confirmed_lower": 0, "possible_upper": 1, "denominator_source_rows": 8,
    }
    assert (pilot["source_rows"], pilot["distinct_dependency_groups"]) == (29, 28)
    assert pilot["status_counts"] == {
        "ALIGNED_NO_CONFLICT": 1,
        "NO_DEMONSTRATED_CONFLICT": 8,
        "POSITIVE": 16,
        "UNRESOLVED": 4,
    }
    assert pilot["conflict_positive_structural_true"] == 4
    assert pilot["conflict_positive_structural_record_bounds"] == {
        "confirmed_lower": 4, "possible_upper": 6, "denominator_source_rows": 16,
    }
    assert pilot["conflict_positive_by_function_family"]["POLLINATOR_ANTAGONIST"]["four_class"] == {
        "SHARED": 7,
    }
    assert pilot["conflict_positive_by_function_family"]["POLLEN_REWARD_GAMETE"]["four_class"] == {
        "STRUCTURAL_MODULE_DIVISION": 3,
    }
    assert pilot["conflict_positive_by_function_family"]["SEXUAL_INTERFERENCE"]["structural_confirmed"] == 1
    assert pilot["conflict_positive_by_function_family"]["SEXUAL_INTERFERENCE"]["structural_unresolved"] == 2
    assert pilot["conflict_positive_by_function_family"]["POLLINATOR_ANTAGONIST"]["structural_unresolved"] == 0


def test_species_only_join_is_prohibited_by_overlap_output():
    audit = analyze()
    overlaps = audit["exact_dependency_group_overlaps"]
    assert [r["exact_dependency_group"] for r in overlaps] == [
        "Ipomopsis_aggregata",
        "Narcissus_assoanus",
        "Polemonium_viscosum",
    ]
    assert all(not row["independent_species_replicate"] for row in overlaps)
    assert all(not row["valid_pooled_fitness_effect"] for row in overlaps)
    rows = {r["exact_dependency_group"]: r for r in overlaps}
    assert rows["Narcissus_assoanus"]["conflict_status_differs"]
    assert rows["Polemonium_viscosum"]["architecture_mode_differs"]
    assert rows["Polemonium_viscosum"]["u2_function_family"] != rows["Polemonium_viscosum"]["pilot_function_family"]
    assert rows["Ipomopsis_aggregata"]["pilot_conflict_status"] == "UNRESOLVED"
    assert audit["historical_Solanum_name_join_held"]


def _copy_source_inputs(tmp_path):
    for p in (U2_PATH, PILOT_PATH):
        dest = tmp_path / p
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / p, dest)


def test_confirmatory_promotion_fails_closed(tmp_path):
    _copy_source_inputs(tmp_path)
    path = tmp_path / U2_PATH
    content = path.read_text(encoding="utf-8")
    assert "SCREENED,false" in content
    path.write_text(content.replace("SCREENED,false", "SCREENED,true", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="SCREENED"):
        analyze(tmp_path)


def test_pilot_structural_proxies_cannot_gain_false_receipt(tmp_path):
    _copy_source_inputs(tmp_path)
    path = tmp_path / PILOT_PATH
    content = path.read_text(encoding="utf-8")
    assert "SHARED_INTEGRATED,false" in content
    path.write_text(content.replace("SHARED_INTEGRATED,false", "SHARED_INTEGRATED,true", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="structural claim"):
        analyze(tmp_path)


def test_unknown_architecture_class_fails_closed(tmp_path):
    _copy_source_inputs(tmp_path)
    path = tmp_path / U2_PATH
    content = path.read_text(encoding="utf-8")
    assert "TEMPORAL_SEPARATION,false" in content
    path.write_text(content.replace("TEMPORAL_SEPARATION,false", "MADE_UP_CLASS,false", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="architecture mode"):
        analyze(tmp_path)


def test_real_cli_runs_in_read_only_stdout_mode():
    script = REPO_ROOT / "scripts/audit_source_stratified_trait_architecture.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    )
    parsed = json.loads(result.stdout)
    assert parsed["u2"]["status_counts"]["POSITIVE"] == 8
    assert parsed["plant_pilot"]["conflict_positive_structural_record_bounds"]["possible_upper"] == 6
    assert parsed["not_pooled"] is True
