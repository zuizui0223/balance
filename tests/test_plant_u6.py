import csv
from pathlib import Path

import pytest

from balance_domain.plant_confirmatory import (
    build_receipt_screening_coverage,
    load_plant_predictor_receipts,
)

from balance_domain.plant_u6 import (
    FORBIDDEN_PASS1_FIELDS,
    build_u6_candidate_adjudication_readout,
    build_u6_evidence_readiness,
    build_u6_multi_batch_readout,
    build_u6_pass2_agreement_from_rows,
    load_u6_anchor,
    load_u6_cross_universe_dependence,
    load_u6_frozen_source_packet,
    load_u6_pass1_freeze_manifest,
    load_u6_pass2_adjudication,
    load_u6_pass2_double_coding,
    load_u6_pass2_source_recovery,
    load_u6_reference_classification,
    u6_source_packet_ready,
    validate_u6_pass1_freeze_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
ANCHOR = ROOT / "data" / "BALANCE_PLANT_U6_REVIEW_ANCHOR_V1.json"
TEMPLATE = ROOT / "data" / "BALANCE_PLANT_U6_REFERENCE_CLASSIFICATION_TEMPLATE_V1.csv"
REFERENCE_BATCHES = [
    ROOT / "data" / f"BALANCE_PLANT_U6_REFERENCE_CLASSIFICATION_BATCH_{x}_V1.csv"
    for x in "ABCD"
]
CANDIDATE_BATCHES = [
    ROOT / "data" / f"BALANCE_PLANT_U6_CANDIDATE_ADJUDICATION_BATCH_{x}_V1.csv"
    for x in "ABC"
]
FREEZE = ROOT / "data" / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json"
PASS2 = ROOT / "data" / "BALANCE_PLANT_U6_PASS2_DOUBLE_CODE_WORKSHEET_V1.csv"
DEPENDENCE = ROOT / "data" / "BALANCE_PLANT_U6_CROSS_UNIVERSE_DEPENDENCE_V1.csv"
SOURCE_PACKET = ROOT / "data" / "BALANCE_PLANT_U6_PASS2_SOURCE_PACKET_V1.csv"
SOURCE_RECOVERY = ROOT / "data" / "BALANCE_PLANT_U6_PASS2_SOURCE_RECOVERY_FRAME_V1.csv"
FROZEN_SOURCE_PACKET = ROOT / "data" / "BALANCE_PLANT_U6_PASS2_FROZEN_SOURCE_PACKET_V1.csv"
PREDICTOR_RECEIPTS = ROOT / "data" / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
ADJUDICATION = ROOT / "data" / "BALANCE_PLANT_U6_PASS2_ADJUDICATION_TEMPLATE_V1.csv"


def test_u6_anchor_keeps_architecture_blinded_in_pass1():
    data = load_u6_anchor(ANCHOR)
    assert data["universe_id"] == "U6_POLLEN_THEFT_HARGREAVES_2009"
    assert set(data["forbidden_during_pass1"]) == FORBIDDEN_PASS1_FIELDS
    assert data["primary_model_admission"].startswith("FORBIDDEN")


def test_u6_reference_template_contains_no_architecture_fields():
    rows = load_u6_reference_classification(TEMPLATE)
    assert len(rows) == 1
    with TEMPLATE.open(encoding="utf-8", newline="") as handle:
        fields = set(csv.DictReader(handle).fieldnames or ())
    assert fields.isdisjoint(FORBIDDEN_PASS1_FIELDS)


def test_u6_pass1_rejects_architecture_leak(tmp_path):
    source = TEMPLATE.read_text(encoding="utf-8")
    lines = source.splitlines()
    lines[0] += ",architecture_mode"
    lines[1] += ",SHARED_INTEGRATED"
    path = tmp_path / "leaked.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="forbidden architecture fields"):
        load_u6_reference_classification(path)


def test_u6_reference_batches_cover_exactly_157_consecutive_references():
    expected_ranges = [(1, 34), (35, 67), (68, 100), (101, 157)]
    for path, (lo, hi) in zip(REFERENCE_BATCHES, expected_ranges):
        rows = load_u6_reference_classification(path)
        assert [row["reference_id"] for row in rows] == [
            f"U6_REF_{i:03d}" for i in range(lo, hi + 1)
        ]
        with path.open(encoding="utf-8", newline="") as handle:
            fields = set(csv.DictReader(handle).fieldnames or ())
        assert fields.isdisjoint(FORBIDDEN_PASS1_FIELDS)

    out = build_u6_multi_batch_readout(REFERENCE_BATCHES)
    assert out["n_references"] == 157
    assert out["first_reference_id"] == "U6_REF_001"
    assert out["last_reference_id"] == "U6_REF_157"
    assert out["reference_status_counts"].get("UNRESOLVED", 0) == 0
    assert out["n_candidates"] == 33
    assert out["architecture_fields_open"] is False
    assert out["pass2_open"] is False


def test_u6_candidate_batches_preserve_screened_decisions():
    a = build_u6_candidate_adjudication_readout(CANDIDATE_BATCHES[0])
    b = build_u6_candidate_adjudication_readout(CANDIDATE_BATCHES[1])
    c = build_u6_candidate_adjudication_readout(CANDIDATE_BATCHES[2])

    assert a["n_adjudication_rows"] == 22
    assert a["decision_counts"] == {
        "EXCLUDE": 4,
        "INCLUDE": 12,
        "RETAIN_UNRESOLVED": 6,
    }
    assert a["n_included_dependency_groups"] == 11

    assert b["n_adjudication_rows"] == 4
    assert b["decision_counts"] == {
        "INCLUDE": 1,
        "RETAIN_UNRESOLVED": 3,
    }
    assert b["included_dependency_groups"] == ["Crescentia_alata"]

    assert c["n_adjudication_rows"] == 9
    assert c["decision_counts"] == {"INCLUDE": 9}
    assert c["n_included_dependency_groups"] == 9

    assert a["pass2_open"] is False
    assert b["pass2_open"] is False
    assert c["pass2_open"] is False


def test_u6_pass1_manifest_matches_executable_reconstruction():
    manifest = load_u6_pass1_freeze_manifest(FREEZE)
    live = validate_u6_pass1_freeze_manifest(
        FREEZE,
        REFERENCE_BATCHES,
        CANDIDATE_BATCHES,
    )

    outcome_ids = set()
    for ids in manifest["candidate_reference_outcomes"].values():
        outcome_ids.update(ids)

    reference_readout = build_u6_multi_batch_readout(REFERENCE_BATCHES)
    assert outcome_ids == set(reference_readout["pollen_theft_candidate_reference_ids"])
    assert len(outcome_ids) == 33

    assert live["status"] == "PASS1_CLOSED"
    assert live["n_references"] == 157
    assert live["n_candidate_references"] == 33
    assert live["n_included_dependency_groups"] == 21
    assert live["n_retained_unresolved_reference_ids"] == 9
    assert live["architecture_used_for_pass1_admission"] is False
    assert live["primary_model_admission"] is False
    assert manifest["status"] == "PASS1_CLOSED_PASS2_CODING_OPEN"
    assert manifest["pass2"]["source_packet_frozen"] is True
    assert manifest["pass2"]["coding_open"] is True
    assert manifest["pass2"]["primary_model_admission"] is False


def test_u6_pass2_worksheet_opens_only_for_frozen_dependency_groups():
    manifest = load_u6_pass1_freeze_manifest(FREEZE)
    rows = load_u6_pass2_double_coding(PASS2, FREEZE)

    assert len(rows) == 42
    assert {row["coder_id"] for row in rows} == {"CODER_A", "CODER_B"}
    assert {row["dependency_group"] for row in rows} == set(
        manifest["included_dependency_groups"]
    )
    assert all(row["coding_status"] == "UNSTARTED" for row in rows)
    assert all(row["architecture_mode"] == "UNRESOLVED" for row in rows)
    assert all(row["module_substrate"] == "UNRESOLVED" for row in rows)
    assert all(row["conflict_timing_geometry"] == "UNRESOLVED" for row in rows)
    assert all(row["conflict_spatial_geometry"] == "UNRESOLVED" for row in rows)


def test_u6_pass2_rejects_nonfrozen_dependency_group(tmp_path):
    source = PASS2.read_text(encoding="utf-8")
    first_group = load_u6_pass1_freeze_manifest(FREEZE)["included_dependency_groups"][0]
    source = source.replace(first_group, "OUTCOME_SELECTED_INTRUDER", 1)
    path = tmp_path / "bad_pass2.csv"
    path.write_text(source, encoding="utf-8")
    with pytest.raises(ValueError, match="non-frozen U6 dependency group"):
        load_u6_pass2_double_coding(path, FREEZE)



def test_u6_cross_universe_dependence_freezes_species_and_taxon_concept_overlap():
    rows = load_u6_cross_universe_dependence(DEPENDENCE, FREEZE)
    species_shared = [
        row for row in rows if row["analysis_action"] == "SHARED_SPECIES_BLOCK"
    ]
    concept_shared = [
        row for row in rows if row["analysis_action"] == "SHARED_TAXON_CONCEPT_BLOCK"
    ]
    assert len(rows) == 21
    assert [(row["u6_dependency_group"], row["overlap_universe"], row["overlap_record_id"])
            for row in species_shared] == [
        ("Impatiens_capensis", "U1", "U1_024")
    ]
    assert [(row["u6_dependency_group"], row["overlap_universe"], row["overlap_record_id"])
            for row in concept_shared] == [
        ("Melastoma_affine", "U3", "U3_PAIR_MELMA_001")
    ]


def test_u6_pass2_source_packet_covers_frozen_groups_without_architecture_columns():
    manifest = load_u6_pass1_freeze_manifest(FREEZE)
    with SOURCE_PACKET.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or ())
        rows = list(reader)

    assert len(rows) == 21
    assert {row["dependency_group"] for row in rows} == set(
        manifest["included_dependency_groups"]
    )
    assert fields.isdisjoint(FORBIDDEN_PASS1_FIELDS)
    assert all("DO_NOT_USE_U6_CANDIDATE_ADJUDICATION_NOTES" in row["coder_instruction"] for row in rows)



def test_u6_pass2_source_recovery_is_frozen_before_coding():
    rows = load_u6_pass2_source_recovery(SOURCE_RECOVERY, FREEZE)
    assert len(rows) == 21
    assert sum(row["source_recovery_status"] == "RESOLVED" for row in rows) == 15
    assert sum(row["source_recovery_status"] == "EVIDENCE_CEILING" for row in rows) == 6
    assert all(row["packet_status"] == "FROZEN" for row in rows)
    assert u6_source_packet_ready(rows) is True


def test_u6_source_recovery_rejects_architecture_targeted_query(tmp_path):
    source = SOURCE_RECOVERY.read_text(encoding="utf-8")
    source = source.replace("floral morphology pollination", "heteranthery pollination", 1)
    path = tmp_path / "leaked_source_search.csv"
    path.write_text(source, encoding="utf-8")
    with pytest.raises(ValueError, match="leaks architecture categories"):
        load_u6_pass2_source_recovery(path, FREEZE)



def test_u6_final_frozen_source_packet_matches_source_recovery_and_manifest():
    rows = load_u6_frozen_source_packet(FROZEN_SOURCE_PACKET, FREEZE, SOURCE_RECOVERY)
    assert len(rows) == 21
    assert all(
        "DO_NOT_USE_U6_ADMISSION_DECISION_NOTES" in row["coder_instruction"]
        for row in rows
    )
    assert sum(row["source_recovery_status"] == "RESOLVED" for row in rows) == 15
    assert sum(row["source_recovery_status"] == "EVIDENCE_CEILING" for row in rows) == 6



def test_u6_agreement_waits_for_completed_independent_coding():
    rows = load_u6_pass2_double_coding(PASS2, FREEZE)
    with pytest.raises(ValueError, match="UNSTARTED"):
        build_u6_pass2_agreement_from_rows(rows)


def test_u6_agreement_report_is_frozen_to_four_pass2_fields():
    manifest = load_u6_pass1_freeze_manifest(FREEZE)
    rows = []
    for group in manifest["included_dependency_groups"]:
        source_refs = ";".join(manifest["source_reference_ids_by_dependency_group"][group])
        for coder in ("CODER_A", "CODER_B"):
            rows.append({
                "dependency_group": group,
                "source_reference_ids": source_refs,
                "coder_id": coder,
                "architecture_mode": "SHARED_INTEGRATED",
                "module_substrate": "SINGLE_OR_CONTINUOUS",
                "conflict_timing_geometry": "SIMULTANEOUS",
                "conflict_spatial_geometry": "SAME_UNIT",
                "coding_status": "CODED",
                "notes": "",
            })
    report = build_u6_pass2_agreement_from_rows(rows)
    assert report["n_dependency_groups"] == 21
    assert set(report["fields"]) == {
        "architecture_mode",
        "module_substrate",
        "conflict_timing_geometry",
        "conflict_spatial_geometry",
    }
    for stats in report["fields"].values():
        assert stats["raw_agreement"] == 1.0
        assert stats["cohen_kappa"] == 1.0
        assert stats["gwet_ac1"] == 1.0
        assert stats["codebook_repair_trigger"] is False
    assert report["confirmatory_promotion_allowed"] is False



def test_u6_predictor_receipt_frame_is_frozen_before_architecture_results():
    rows = load_plant_predictor_receipts(PREDICTOR_RECEIPTS)
    assert len(rows) == 63
    assert len({row["cluster_id"] for row in rows}) == 21
    by_cluster = {}
    for row in rows:
        by_cluster.setdefault(row["cluster_id"], set()).add(row["predictor"])
        assert row["reported_value"] == "UNRESOLVED"
        assert row["evidence_type"] == "UNCLEAR"
        assert row["outcome_independence"] == "UNCERTAIN"
        assert row["adjudication_status"] == "SCREENED"
    assert all(predictors == {
        "module_substrate",
        "conflict_timing_geometry",
        "conflict_spatial_geometry",
    } for predictors in by_cluster.values())

    coverage = build_receipt_screening_coverage(rows)
    assert coverage["n_receipts"] == 63
    assert coverage["n_clusters"] == 21
    assert coverage["n_complete_outcome_independent_clusters"] == 0
    assert coverage["n_complete_adjudicated_clusters"] == 0



def test_u6_adjudication_template_stays_pending_before_coder_completion():
    coding_rows = load_u6_pass2_double_coding(PASS2, FREEZE)
    rows = load_u6_pass2_adjudication(ADJUDICATION, FREEZE, coding_rows)
    assert len(rows) == 21
    assert all(row["adjudication_status"] == "PENDING" for row in rows)
    assert all(row["adjudication_basis"] == "AWAITING_INDEPENDENT_DOUBLE_CODING" for row in rows)
    assert all(row["architecture_mode"] == "UNRESOLVED" for row in rows)
    assert all(row["module_substrate"] == "UNRESOLVED" for row in rows)
    assert all(row["conflict_timing_geometry"] == "UNRESOLVED" for row in rows)
    assert all(row["conflict_spatial_geometry"] == "UNRESOLVED" for row in rows)


def test_u6_adjudication_cannot_preempt_independent_coding(tmp_path):
    source = ADJUDICATION.read_text(encoding="utf-8")
    source = source.replace(
        ",UNRESOLVED,UNRESOLVED,UNRESOLVED,UNRESOLVED,PENDING,AWAITING_INDEPENDENT_DOUBLE_CODING,",
        ",SHARED_INTEGRATED,SINGLE_OR_CONTINUOUS,SIMULTANEOUS,SAME_UNIT,ADJUDICATED,SOURCE_REVIEW,preemptive",
        1,
    )
    path = tmp_path / "preemptive_adjudication.csv"
    path.write_text(source, encoding="utf-8")
    coding_rows = load_u6_pass2_double_coding(PASS2, FREEZE)
    with pytest.raises(ValueError, match="before both independent coder rows are CODED"):
        load_u6_pass2_adjudication(path, FREEZE, coding_rows)



def test_u6_current_evidence_readiness_reports_exact_open_gates():
    coding = load_u6_pass2_double_coding(PASS2, FREEZE)
    adjudication = load_u6_pass2_adjudication(ADJUDICATION, FREEZE, coding)
    receipts = load_plant_predictor_receipts(PREDICTOR_RECEIPTS)
    dependence = load_u6_cross_universe_dependence(DEPENDENCE, FREEZE)

    out = build_u6_evidence_readiness(coding, adjudication, receipts, dependence)
    assert out["coding_complete"] is False
    assert out["reliability_pass"] is False
    assert out["adjudication_complete"] is False
    assert out["n_groups_with_three_adjudicated_independent_predictors"] == 0
    assert out["predictor_receipts_complete"] is False
    assert out["dependence_map_complete"] is True
    assert out["ready_for_combined_model_assembly"] is False
    assert out["blockers"] == [
        "independent_double_coding_incomplete",
        "post_coding_adjudication_incomplete",
        "outcome_independent_predictor_receipts_incomplete:0/21",
    ]
    assert out["combined_model_estimability_checked"] is False


def test_u6_evidence_readiness_can_close_without_claiming_combined_estimability():
    manifest = load_u6_pass1_freeze_manifest(FREEZE)
    groups = manifest["included_dependency_groups"]
    coding = []
    adjudication = []
    receipts = []
    for group in groups:
        source_refs = ";".join(manifest["source_reference_ids_by_dependency_group"][group])
        for coder in ("CODER_A", "CODER_B"):
            coding.append({
                "dependency_group": group,
                "source_reference_ids": source_refs,
                "coder_id": coder,
                "architecture_mode": "SHARED_INTEGRATED",
                "module_substrate": "SINGLE_OR_CONTINUOUS",
                "conflict_timing_geometry": "SIMULTANEOUS",
                "conflict_spatial_geometry": "SAME_UNIT",
                "coding_status": "CODED",
                "notes": "",
            })
        adjudication.append({
            "dependency_group": group,
            "architecture_mode": "SHARED_INTEGRATED",
            "module_substrate": "SINGLE_OR_CONTINUOUS",
            "conflict_timing_geometry": "SIMULTANEOUS",
            "conflict_spatial_geometry": "SAME_UNIT",
            "adjudication_status": "ADJUDICATED",
            "adjudication_basis": "SOURCE_REVIEW_AFTER_AGREEMENT",
            "notes": "synthetic gate test",
        })
        for i, (predictor, value) in enumerate((
            ("module_substrate", "SINGLE_OR_CONTINUOUS"),
            ("conflict_timing_geometry", "SIMULTANEOUS"),
            ("conflict_spatial_geometry", "SAME_UNIT"),
        )):
            receipts.append({
                "receipt_id": f"{group}_{i}",
                "cluster_id": group,
                "predictor": predictor,
                "reported_value": value,
                "source_id": "synthetic",
                "evidence_type": "PRE_OUTCOME_MEASUREMENT",
                "outcome_independence": "TRUE",
                "adjudication_status": "ADJUDICATED",
                "notes": "",
            })

    dependence = load_u6_cross_universe_dependence(DEPENDENCE, FREEZE)
    out = build_u6_evidence_readiness(coding, adjudication, receipts, dependence)
    assert out["coding_complete"] is True
    assert out["reliability_pass"] is True
    assert out["adjudication_complete"] is True
    assert out["predictor_receipts_complete"] is True
    assert out["ready_for_combined_model_assembly"] is True
    assert out["combined_model_estimability_checked"] is False
