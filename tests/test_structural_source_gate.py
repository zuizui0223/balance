"""Primary-source claim-ceiling checks; candidate data are literature, not field receipts."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from balance_domain.structural_source_gate import (
    EVIDENCE_KEYS,
    STATE_MISSING,
    STATE_VERIFIED,
    adjudicate_structural_registry,
    adjudicate_structural_source,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/BALANCE_STRUCTURAL_WORLDLINE_SOURCE_AUDIT_V1.json"


def registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_five_source_candidates_stay_outside_direct_structural_receipt():
    result = adjudicate_structural_registry(registry())
    assert result["candidate_count"] == 5
    assert result["source_eligible_count"] == 0
    assert result["direct_structural_worldline_receipt_count"] == 0
    assert result["independent_biological_clusters_added"] == 0
    assert result["outcome_fitness_values_reconstructed"] is False
    assert all(x["status"] == "SOURCE_COMPARATOR_HOLD" for x in result["results"])
    assert all(x["balance_occupancy_identified"] is False for x in result["results"])
    assert all(x["direct_worldline_gap_estimated"] is False for x in result["results"])


def test_solanum_anther_function_evidence_is_not_matched_architecture_fitness():
    result = registry()["candidates"][1]
    assert result["system"].startswith("Solanum rostratum")
    assert result["evidence"]["structural_intervention_or_architecture_identity_verified"]["status"] == STATE_VERIFIED
    assert result["evidence"]["matched_shared_structural_worldline"]["status"] == STATE_MISSING
    assert "NOT_A_REGISTERED_NET_STRUCTURAL_COMPARATOR" in (
        adjudicate_structural_source(result).missing_gates
    )


def test_dalechampia_seed_only_cost_does_not_promote_net_fitness():
    row = next(x for x in registry()["candidates"] if x["candidate_id"] == "DAL_SCAN_REWARD")
    assert row["evidence"]["same_biological_context"]["status"] == STATE_VERIFIED
    assert row["evidence"]["common_net_whole_system_fitness_scale"]["status"] == STATE_MISSING


def test_cogfp_structural_control_does_not_turn_facs_into_fitness():
    row = next(x for x in registry()["candidates"] if x["candidate_id"] == "COGFP_1V2")
    assert row["comparison_class"] == "STRUCTURAL_NONNESTED"
    assert row["evidence"]["same_biological_context"]["status"] == STATE_VERIFIED
    assert row["evidence"]["common_net_whole_system_fitness_scale"]["status"] == STATE_MISSING
    assert row["evidence"]["positive_sch_conflict_on_fitness_scale"]["status"] == STATE_MISSING


def test_nested_uncosted_superworld_never_is_direct_structural_candidate():
    row = copy.deepcopy(registry()["candidates"][3])
    row["candidate_id"] = "SYNTHETIC_NESTED_UNCOSTED"
    row["comparison_class"] = "NESTED_UNCOSTED_ENVELOPE"
    for evidence in row["evidence"].values():
        evidence["status"] = STATE_VERIFIED
    assert adjudicate_structural_source(row).status == "SOURCE_COMPARATOR_HOLD"
    assert "NOT_A_REGISTERED_NET_STRUCTURAL_COMPARATOR" in (
        adjudicate_structural_source(row).missing_gates
    )


def test_nested_architecture_requires_net_cost_in_same_fitness_scale():
    row = copy.deepcopy(registry()["candidates"][3])
    row["candidate_id"] = "SYNTHETIC_NESTED_COSTED"
    row["comparison_class"] = "STRUCTURAL_NESTED_NET_COSTED"
    for evidence in row["evidence"].values():
        evidence["status"] = STATE_VERIFIED
    assert "MISSING_NET_NESTED_ARCHITECTURE_COST" in (
        adjudicate_structural_source(row).missing_gates
    )
    row["net_architecture_cost_in_fitness"] = True
    outcome = adjudicate_structural_source(row)
    assert outcome.status == "SOURCE_COMPARATOR_ELIGIBLE_FOR_WORLDLINE_TEST_NOT_BALANCE"
    assert outcome.balance_occupancy_identified is False
    assert outcome.direct_worldline_gap_estimated is False


def test_all_claim_source_proof_gates_must_be_accounted_for():
    row = copy.deepcopy(registry()["candidates"][3])
    row["candidate_id"] = "SYNTHETIC_NONNESTED_ELIGIBLE"
    for evidence in row["evidence"].values():
        evidence["status"] = STATE_VERIFIED
    result = adjudicate_structural_source(row)
    assert result.status == "SOURCE_COMPARATOR_ELIGIBLE_FOR_WORLDLINE_TEST_NOT_BALANCE"
    assert result.missing_gates == ()
    assert result.balance_occupancy_identified is False
    assert result.contributes_new_independent_biological_cluster is False
    assert result.structural_architecture_cost_identified_by_audit is False


def test_missing_evidence_source_basis_or_gates_fail_closed():
    row = copy.deepcopy(registry()["candidates"][0])
    row["evidence"][EVIDENCE_KEYS[0]]["source_basis"] = ""
    with pytest.raises(ValueError, match="source_basis"):
        adjudicate_structural_source(row)
    row = copy.deepcopy(registry()["candidates"][0])
    row["evidence"].pop(EVIDENCE_KEYS[0])
    with pytest.raises(ValueError, match="field set"):
        adjudicate_structural_source(row)
    row = copy.deepcopy(registry()["candidates"][0])
    row["evidence"][EVIDENCE_KEYS[0]]["status"] = True
    with pytest.raises(ValueError, match="unsupported evidence status"):
        adjudicate_structural_source(row)


def test_duplicate_candidates_and_wrong_scope_fail_closed():
    data = registry()
    data["candidates"].append(copy.deepcopy(data["candidates"][0]))
    with pytest.raises(ValueError, match="duplicate"):
        adjudicate_structural_registry(data)
    data = registry()
    data["status"] = "FIELD_BALANCE_POSITIVE"
    with pytest.raises(ValueError, match="curated"):
        adjudicate_structural_registry(data)


def test_unverified_physical_trait_state_not_promoted_by_narrative():
    row = copy.deepcopy(registry()["candidates"][2])
    assert row["evidence"]["structural_intervention_or_architecture_identity_verified"]["status"] == STATE_MISSING
    assert adjudicate_structural_source(row).status == "SOURCE_COMPARATOR_HOLD"


def test_machine_source_audit_is_only_eligibility_not_new_pooled_replication():
    data = registry()
    result = adjudicate_structural_registry(data)
    assert all(x["analysis_kind"] == "SOURCE_ELIGIBILITY_ONLY_NOT_EMPIRICAL_WORLDLINE"
               for x in result["results"])
    assert all(x["contributes_new_independent_biological_cluster"] is False
               for x in result["results"])


def test_hashed_source_runner_is_reproducible_and_never_overwrites(tmp_path):
    import hashlib
    from scripts.audit_structural_worldline_sources import run_source_audit

    target = tmp_path / "readout.json"
    before = REGISTRY.read_bytes()
    result = run_source_audit(REGISTRY, target)
    assert target.exists()
    assert result["source_registry_sha256"] == hashlib.sha256(before).hexdigest()
    assert result["status"] == "SOURCE_ELIGIBILITY_AUDIT_ONLY"
    assert result["source_eligible_count"] == 0
    assert REGISTRY.read_bytes() == before
    assert json.loads(target.read_text(encoding="utf-8")) == result
    with pytest.raises(ValueError, match="already exists"):
        run_source_audit(REGISTRY, target)
