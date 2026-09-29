import csv
import pytest
from pathlib import Path

from balance_domain.plant_u2 import (
    build_u2_readout,
    build_u2_double_code_handoff,
    build_u2_reference_handoff,
    load_u2_adjudication,
    load_u2_blank_worksheet,
    load_u2_double_code_sample,
    load_u2_universe,
)


ROOT = Path(__file__).resolve().parents[1]
U2 = ROOT / "data" / "BALANCE_PLANT_U2_BARRETT_REVIEW_UNIVERSE_V1.csv"
COVERAGE = ROOT / "data" / "BALANCE_PLANT_U2_REFERENCE_COVERAGE_V1.csv"
SAMPLE = ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SAMPLE_V1.csv"
PACKET = ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_SOURCE_PACKET_V1.csv"
WORKSHEET = ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_WORKSHEET_V1.csv"
ADJUDICATION = ROOT / "data" / "BALANCE_PLANT_U2_DOUBLE_CODE_ADJUDICATION_TEMPLATE_V1.csv"


def test_u2_review_universe_validates():
    rows = load_u2_universe(U2)
    assert len(rows) == 22
    assert len({r["dependency_group"] for r in rows}) == 22


def test_u2_is_discovery_only_even_when_source_resolution_is_closed():
    readout = build_u2_readout(U2)
    assert readout["n_registered_dependency_groups"] == 22
    assert readout["n_species_level_source_resolved"] == 22
    assert readout["n_taxon_resolution_pending"] == 0
    assert "not_conflict_positive" in readout["claim_ceiling"]


def test_u2_reference_coverage_and_source_handoff_are_closed():
    handoff = build_u2_reference_handoff(U2, COVERAGE)
    assert handoff["n_registered_dependency_groups"] == 22
    assert handoff["n_barrett_references"] == 37
    assert handoff["n_pending_reference_classifications"] == 0
    assert handoff["n_unresolved_primary_sources"] == 0
    assert handoff["review_reference_coverage_closed"] is True
    assert handoff["species_source_resolution_closed"] is True
    assert handoff["discovery_universe_source_closed"] is True
    assert "not_conflict_status" in handoff["claim_ceiling"]


def test_eichhornia_multiple_studies_are_one_dependency_group():
    rows = load_u2_universe(U2)
    eich = [r for r in rows if r["dependency_group"] == "Eichhornia_paniculata"]
    assert len(eich) == 1
    assert "Kohn_Barrett_1992" in eich[0]["review_reference"]
    assert "Harder_Barrett_1995" in eich[0]["review_reference"]
    assert "Harder_Barrett_Cole_2000" in eich[0]["review_reference"]


def test_review_universe_retains_null_or_specificity_case():
    rows = load_u2_universe(U2)
    pont = next(r for r in rows if r["dependency_group"] == "Pontederia_cordata")
    assert pont["evidence_family"] == "PHYSICAL_SEX_ORGAN_INTERFERENCE_NULL_TEST"
    assert pont["screening_status"] == "SCREENED"


def test_alpinia_flexistyly_program_is_resolved_to_species():
    rows = load_u2_universe(U2)
    alpinia = next(r for r in rows if r["dependency_group"] == "Alpinia_kwangsiensis")
    assert alpinia["taxon_raw"] == "Alpinia kwangsiensis"
    assert alpinia["source_resolution_status"] == "RESOLVED_PRIMARY"
    assert alpinia["primary_source_doi"] == "10.1038/35068635"


def test_u2_source_closed_first20_is_ready_for_independent_double_coding():
    handoff = build_u2_double_code_handoff(U2, SAMPLE, PACKET, WORKSHEET)
    assert handoff["n_universe_groups"] == 22
    assert handoff["n_sampled_groups"] == 20
    assert handoff["n_source_packet_groups"] == 20
    assert handoff["n_blank_worksheet_rows"] == 40
    assert handoff["all_sampled_sources_resolved"] is True
    assert handoff["selection_rule_closed"] is True
    assert handoff["source_packet_blinded_to_review_evidence_family"] is True
    assert handoff["two_independent_coder_slots_per_group"] is True
    assert handoff["independent_double_coding_ready"] is True


def test_u2_double_code_sample_retains_preregistered_record_id_first20():
    rows = load_u2_double_code_sample(SAMPLE)
    assert [r["universe_record_id"] for r in rows] == [
        f"U2_{i:03d}" for i in range(1, 21)
    ]
    assert rows[8]["taxon_raw"] == "Wahlenbergia albomarginata"
    assert rows[19]["taxon_raw"] == "Wachendorfia thyrsiflora"
    assert all(
        r["selection_rule"] == "FIRST_20_DEPENDENCY_GROUPS_BY_FROZEN_U2_RECORD_ID"
        for r in rows
    )



def test_u2_blank_worksheet_has_two_empty_coder_rows_per_sample_group():
    sample_groups = {row["dependency_group"] for row in load_u2_double_code_sample(SAMPLE)}
    rows = load_u2_blank_worksheet(WORKSHEET)
    assert len(rows) == 40
    assert {row["cluster_id"] for row in rows} == sample_groups
    for group in sample_groups:
        pair = [row for row in rows if row["cluster_id"] == group]
        assert {row["coder_id"] for row in pair} == {"CODER_A", "CODER_B"}
        for row in pair:
            assert not row["conflict_status"]
            assert not row["architecture_mode"]
            assert not row["module_substrate"]
            assert not row["conflict_timing_geometry"]
            assert not row["conflict_spatial_geometry"]



def test_u2_adjudication_template_remains_pending_before_double_coding():
    sample = load_u2_double_code_sample(SAMPLE)
    rows = load_u2_adjudication(ADJUDICATION, sample)
    assert len(rows) == 20
    assert all(row["adjudication_status"] == "PENDING" for row in rows)
    assert all(row["adjudication_basis"] == "AWAITING_INDEPENDENT_DOUBLE_CODING" for row in rows)
    assert all(row["conflict_status"] == "UNRESOLVED" for row in rows)
    assert all(row["architecture_mode"] == "UNRESOLVED" for row in rows)
    assert all(row["module_substrate"] == "UNRESOLVED" for row in rows)
    assert all(row["conflict_timing_geometry"] == "UNRESOLVED" for row in rows)
    assert all(row["conflict_spatial_geometry"] == "UNRESOLVED" for row in rows)


def test_u2_adjudication_cannot_preempt_two_completed_coders(tmp_path):
    source = ADJUDICATION.read_text(encoding="utf-8")
    source = source.replace(
        ",UNRESOLVED,UNRESOLVED,UNRESOLVED,UNRESOLVED,UNRESOLVED,PENDING,AWAITING_INDEPENDENT_DOUBLE_CODING,",
        ",POSITIVE,SHARED_INTEGRATED,SINGLE_OR_CONTINUOUS,SIMULTANEOUS,SAME_UNIT,ADJUDICATED,SOURCE_REVIEW,preemptive",
        1,
    )
    path = tmp_path / "bad_u2_adjudication.csv"
    path.write_text(source, encoding="utf-8")
    sample = load_u2_double_code_sample(SAMPLE)
    with pytest.raises(ValueError, match="before two completed coder rows exist"):
        load_u2_adjudication(path, sample)



def test_u2_low_agreement_blocks_adjudication(tmp_path):
    sample = load_u2_double_code_sample(SAMPLE)
    coding = []
    for i, row in enumerate(sample):
        group = row["dependency_group"]
        for coder in ("CODER_A", "CODER_B"):
            coding.append({
                "cluster_id": group,
                "coder_id": coder,
                "conflict_status": "NO_DEMONSTRATED_CONFLICT",
                "architecture_mode": (
                    "SHARED_INTEGRATED"
                    if coder == "CODER_A" or i >= 5
                    else "TEMPORAL_SEPARATION"
                ),
                "module_substrate": "SINGLE_OR_CONTINUOUS",
                "conflict_timing_geometry": "SIMULTANEOUS",
                "conflict_spatial_geometry": "SAME_UNIT",
                "notes": "synthetic agreement gate",
            })

    with ADJUDICATION.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows[0].update({
        "conflict_status": "NO_DEMONSTRATED_CONFLICT",
        "architecture_mode": "SHARED_INTEGRATED",
        "module_substrate": "SINGLE_OR_CONTINUOUS",
        "conflict_timing_geometry": "SIMULTANEOUS",
        "conflict_spatial_geometry": "SAME_UNIT",
        "adjudication_status": "ADJUDICATED",
        "adjudication_basis": "SOURCE_REVIEW",
        "notes": "synthetic adjudication",
    })
    path = tmp_path / "u2_low_agreement_adjudication.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    with pytest.raises(ValueError, match="codebook repair/recode"):
        load_u2_adjudication(path, sample, coding)



def test_u2_completed_coding_groups_must_match_frozen_sample():
    sample = load_u2_double_code_sample(SAMPLE)
    coding = []
    for row in sample:
        group = row["dependency_group"]
        for coder in ("CODER_A", "CODER_B"):
            coding.append({
                "cluster_id": group,
                "coder_id": coder,
                "conflict_status": "NO_DEMONSTRATED_CONFLICT",
                "architecture_mode": "SHARED_INTEGRATED",
                "module_substrate": "SINGLE_OR_CONTINUOUS",
                "conflict_timing_geometry": "SIMULTANEOUS",
                "conflict_spatial_geometry": "SAME_UNIT",
                "notes": "synthetic identity gate",
            })
    original = sample[0]["dependency_group"]
    for row in coding:
        if row["cluster_id"] == original:
            row["cluster_id"] = "NON_FROZEN_INTRUDER"

    with pytest.raises(ValueError, match="exactly match the frozen reliability sample"):
        load_u2_adjudication(ADJUDICATION, sample, coding)
