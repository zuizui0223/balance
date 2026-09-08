import csv
import json
from pathlib import Path

import pytest

from scripts.build_q1b_identification_gap_readout import build


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "BALANCE_Q1B_IDENTIFICATION_GAP_LEDGER_V1.csv"
READOUT = ROOT / "data" / "BALANCE_Q1B_IDENTIFICATION_GAP_READOUT_V1.json"
STRATA = ROOT / "data" / "BALANCE_QUANTITATIVE_STRATA_V1.csv"


def test_q1b_gap_readout_is_deterministic_and_synced():
    observed = build(LEDGER)
    frozen = json.loads(READOUT.read_text(encoding="utf-8"))
    assert observed == frozen


def test_only_fragaria_passes_strict_effect_ready_q1b_gate():
    result = build(LEDGER)
    assert result["n_audited_programmes"] == 15
    assert result["n_strict_q1b_effect_ready"] == 1
    assert result["strict_q1b_effect_ready_studies"] == ["EGAN_FRAGARIA_2021"]
    assert result["n_nonpass_programmes"] == 14
    assert result["pooling_implication"] == "one_effect_ready_positive_is_below_three_cluster_pooling_gate"


def test_gap_audit_retains_negative_controls_and_distinct_failure_modes():
    result = build(LEDGER)
    assert result["n_design_matched_negative_controls"] == 2
    assert result["q1b_class_counts"]["FACTORIAL_NEGATIVE_CONTROL"] == 2
    assert result["q1b_class_counts"]["ADDITIVE_OPPOSITION_SIMPLE_Q1"] == 1
    assert result["q1b_class_counts"]["DISCRETE_MORPH_OPPOSITION"] == 1
    assert result["q1b_class_counts"]["HERBIVORY_PLASTICITY_CONTEXT"] == 1
    assert result["first_failed_gate_counts"]["same_trait_opposition_absent"] == 2
    assert result["first_failed_gate_counts"]["independent_antagonist_selection_absent"] == 2
    assert result["first_failed_gate_counts"]["antagonist_manipulation_absent"] == 2


def test_claim_ceiling_is_design_coverage_not_prevalence():
    result = build(LEDGER)
    assert result["claim_ceiling"] == (
        "targeted_design_coverage_audit_not_natural_prevalence_"
        "or_exhaustive_global_systematic_review"
    )


def test_q1b_stratum_routes_future_search_through_gap_ledger():
    with STRATA.open(encoding="utf-8", newline="") as handle:
        rows = {row["stratum_id"]: row for row in csv.DictReader(handle)}
    q1b = rows["DIFFUSE_FACTORIAL_AGENT_SELECTION"]
    assert q1b["registered_pattern_candidates"] == "1"
    assert q1b["effect_size_ready_clusters"] == "1"
    assert q1b["min_independent_clusters"] == "3"
    assert "BALANCE_Q1B_IDENTIFICATION_GAP_LEDGER_V1" in q1b["next_gate"]
    assert "without_relaxing_failed_gates" in q1b["next_gate"]


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "study_key",
        "system_taxon",
        "q1b_class",
        "first_failed_gate",
        "claim_ceiling",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_duplicate_study_keys_fail_closed(tmp_path):
    path = tmp_path / "duplicate.csv"
    row = {
        "study_key": "X",
        "system_taxon": "taxon",
        "q1b_class": "FACTORIAL_NEGATIVE_CONTROL",
        "first_failed_gate": "same_trait_opposition_absent",
        "claim_ceiling": "bounded",
    }
    _write_rows(path, [row, row])
    with pytest.raises(ValueError, match="duplicate study_key"):
        build(path)


def test_pass_class_and_pass_gate_must_agree(tmp_path):
    path = tmp_path / "mismatch.csv"
    _write_rows(
        path,
        [
            {
                "study_key": "X",
                "system_taxon": "taxon",
                "q1b_class": "STRICT_Q1B_EFFECT_READY",
                "first_failed_gate": "same_trait_opposition_absent",
                "claim_ceiling": "bounded",
            }
        ],
    )
    with pytest.raises(ValueError, match="pass-state mismatch"):
        build(path)
