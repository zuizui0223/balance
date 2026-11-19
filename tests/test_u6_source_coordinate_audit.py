"""Read-only U6 pollen-stage evidence audits: source and inference firewall."""
from pathlib import Path

import pytest

from balance_domain.u6_source_coordinate_audit import build_u6_source_coordinate_audit

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PASS1 = DATA / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json"
BATCHES = [
    DATA / f"BALANCE_PLANT_U6_CANDIDATE_ADJUDICATION_BATCH_{c}_V1.csv"
    for c in "ABC"
]
FLAGS = DATA / "BALANCE_U6_POSTOPEN_STAGE_REVIEW_FLAGS_20261119.csv"
U2_SCREEN = DATA / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv"
U2_RECEIPTS = DATA / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
U6_RECEIPTS = DATA / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"


def run(*, batches=BATCHES, flags=FLAGS, u6_receipts=U6_RECEIPTS):
    return build_u6_source_coordinate_audit(
        PASS1, batches, flags, U2_SCREEN, U2_RECEIPTS, u6_receipts
    )


def test_full_21_group_evidence_ladder_is_preserved_without_double_counting():
    result = run()
    assert result["frozen_u6_group_count"] == 21
    assert result["included_source_receipt_type_counts_by_unique_group"] == {
        "DIRECT_CONSUMPTION_AVAILABLE_POLLEN_LOSS": 5,
        "DIRECT_REMOVAL_FITNESS_COST": 4,
        "DIRECT_POLLEN_ROBBING_NO_POLLINATION": 10,
        "DIRECT_REMOVAL_LOW_DEPOSITION": 2,
    }
    assert result["fitness_tag_groups"] == [
        "Campanula_americana", "Clusia_arrudae",
        "Grevillea_barklyana", "Melastoma_affine"
    ]


def test_primary_source_reference_identity_retains_shared_and_repeated_studies():
    depend = run()["source_reference_dependence"]
    assert depend["included_adjudication_rows"] == 22
    assert depend["included_unique_primary_reference_ids"] == 21
    assert depend["source_refs_spanning_multiple_groups"] == {
        "U6_REF_078": ["Actinidia_deliciosa", "Echium_plantagineum"]
    }
    assert depend["groups_supported_by_multiple_source_refs"] == {
        "Theobroma_cacao": ["U6_REF_153", "U6_REF_155"]
    }


def test_stage_flags_do_not_relabel_21_source_screened_predictor_groups():
    data = run()
    assert set(data["postopen_review_flags"]) == {
        "Melastoma_affine", "Nothofagus_pumilio", "Zea_mays"
    }
    assert data["original_source_reference_map_unchanged"] is True
    assert data["all_frozen_u6_primary_references_retained"] is True
    assert data["architecture_outcomes_accessed"] is False
    assert data["predictor_adjudications_performed"] is False
    assert data["v4_fit_performed"] is False


def test_frozen_vs_hypothetical_stage_filters_have_exact_v4_support():
    m = run()["scenario_summary"]
    expected = {
        "FROZEN_ALL": (21, 29, 18, 3, True),
        "POSTOPEN_REMOVE_TWO_STAGE_MISMATCHES": (19, 27, 16, 3, True),
        "POSTOPEN_REMOVE_STAGE_AND_BUNDLED_FLOWER": (18, 26, 15, 3, True),
        "SOURCE_ADMISSION_FITNESS_TAG_ONLY": (4, 12, 3, 1, False),
        "FITNESS_TAG_WITHOUT_HARD_STAGE_MISMATCH": (3, 11, 2, 1, False),
    }
    assert set(m) == set(expected)
    for key, (u6, total, simultaneous, ordered, ordered_supported) in expected.items():
        row = m[key]
        assert row["u6_included_groups_after_hypothetical_filter"] == u6
        assert row["pooled_source_screened_groups"] == total
        assert row["u6_screened_timing"] == {
            "SIMULTANEOUS": simultaneous,
            "ORDERED_OR_ALTERNATING": ordered,
        }
        assert row["u6_has_two_ordered_groups"] is ordered_supported
        assert row["full_design_rank"] == 5
        assert row["slope_design_rank"] == 3
        assert row["frozen_min_primary_level_support"] == {
            "module": True, "timing": True
        }
        # Frozen V1 has only one U2 SINGLE + SIMULTANEOUS group.
        assert row["g1_predictor_common_support_only"] is False


def test_accepted_reference_tamper_fails_closed(tmp_path):
    raw = BATCHES[0].read_text(encoding="utf-8")
    assert "U6_ADJ_031,U6_REF_031" in raw
    changed = raw.replace(
        "U6_ADJ_031,U6_REF_031", "U6_ADJ_031,TAMPERED_REF", 1
    )
    wrong = tmp_path / "tampered_adjudication.csv"
    wrong.write_text(changed, encoding="utf-8")
    with pytest.raises(ValueError, match="references differ"):
        run(batches=[wrong, BATCHES[1], BATCHES[2]])


def test_flag_mutation_fails_closed_not_fitted_exclusion(tmp_path):
    text = FLAGS.read_text(encoding="utf-8")
    assert "RECIPIENT_STIGMA" in text
    altered = text.replace("RECIPIENT_STIGMA", "SOURCE_ANTHER", 1)
    wrong = tmp_path / "incorrect_flag.csv"
    wrong.write_text(altered, encoding="utf-8")
    with pytest.raises(ValueError, match="Unexpected post-open stage flag"):
        run(flags=wrong)


def test_preemptive_u6_adjudication_fails_closed(tmp_path):
    raw = U6_RECEIPTS.read_text(encoding="utf-8")
    assert ",SCREENED," in raw
    wrong = tmp_path / "u6_made_up_adjudication.csv"
    wrong.write_text(raw.replace(",SCREENED,", ",ADJUDICATED,", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="SCREENED receipts only"):
        run(u6_receipts=wrong)
