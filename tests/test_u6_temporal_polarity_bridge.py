"""Checks that visitor-order polarity is not a substitute for measured fitness."""
from pathlib import Path

import pytest

from balance_domain.u6_temporal_polarity_bridge import (
    build_u6_temporal_polarity_bridge,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PASS1 = DATA / "BALANCE_PLANT_U6_PASS1_FREEZE_V1.json"
BATCHES = [
    DATA / f"BALANCE_PLANT_U6_CANDIDATE_ADJUDICATION_BATCH_{letter}_V1.csv"
    for letter in "ABC"
]
ORDER = DATA / "BALANCE_U6_TEMPORAL_POLARITY_CROSSWALK_20261119.csv"
FLAGS = DATA / "BALANCE_U6_POSTOPEN_STAGE_REVIEW_FLAGS_20261119.csv"
U2_SCREEN = DATA / "BALANCE_PLANT_U2_CONFLICT_SCREEN_V1.csv"
U2_RECEIPTS = DATA / "BALANCE_PLANT_U2_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"
U6_RECEIPTS = DATA / "BALANCE_PLANT_U6_CONFIRMATORY_PREDICTOR_RECEIPT_FRAME_V1.csv"


def run(*, order=ORDER, u6_receipts=U6_RECEIPTS):
    return build_u6_temporal_polarity_bridge(
        PASS1, BATCHES, order, FLAGS,
        U2_SCREEN, U2_RECEIPTS, u6_receipts,
    )


def test_original_three_ordered_cases_have_two_opposite_polarities():
    r = run()
    assert r["original_u6_source_screened_group_count"] == 21
    assert r["original_u6_sequential_source_group_count"] == 3
    assert r["source_poles"] == {
        "THEFT_BEFORE_EFFECTIVE_TRANSFER": [
            "Clusia_arrudae", "Crescentia_alata"
        ],
        "EFFECTIVE_TRANSFER_BEFORE_THEFT": ["Tolmiea_menziesii"],
    }
    assert r["source_lineage"] == (
        "PR252_PRIOR_SOURCE_LEDGER_REUSED_NOT_INDEPENDENT_REPLICATION"
    )


def test_only_one_sequential_group_was_admitted_with_fitness_related_evidence():
    r = run()
    assert r["original_admission_fitness_tag_within_sequential"] == [
        "Clusia_arrudae"
    ]
    assert r[
        "study_level_fitness_admission_tag_not_causal_pollen_specific_effect"
    ] is True
    assert "need not have exported all available pollen" in r["biological_limit"]


def test_leave_each_sequential_group_out_does_not_repair_polarity_support():
    r = run()["exact_source_order_leave_one_out"]
    assert len(r) == 4
    assert r["FROZEN_ALL"]["source_polarity_counts"] == {
        "THEFT_BEFORE_EFFECTIVE_TRANSFER": 2,
        "EFFECTIVE_TRANSFER_BEFORE_THEFT": 1,
    }
    assert all(x["source_screened_v4_rank"] == 5 for x in r.values())
    assert all(x["ordered_poles_each_with_min_two_sources"] is False
               for x in r.values())
    assert all(x["frozen_g1_predictor_common_support_only"] is False
               for x in r.values())
    for key, x in r.items():
        if key != "FROZEN_ALL":
            assert x["u6_ordered_source_groups"] == 2
            assert x["frozen_u6_ordered_min_two_sources"] is True


def test_early_and_late_deletions_have_distinct_source_support_semantics():
    r = run()["exact_source_order_leave_one_out"]
    no_late = r["HYPOTHETICAL_REMOVE_TOLMIEA_MENZIESII"]
    assert no_late["source_polarity_counts"] == {
        "THEFT_BEFORE_EFFECTIVE_TRANSFER": 2,
        "EFFECTIVE_TRANSFER_BEFORE_THEFT": 0,
    }
    no_early_fitness = r["HYPOTHETICAL_REMOVE_CLUSIA_ARRUDAE"]
    assert no_early_fitness["source_polarity_counts"] == {
        "THEFT_BEFORE_EFFECTIVE_TRANSFER": 1,
        "EFFECTIVE_TRANSFER_BEFORE_THEFT": 1,
    }
    assert no_early_fitness[
        "ordered_groups_with_original_fitness_admission_tag"
    ] == []


def test_crosswalk_doi_relabeling_is_rejected(tmp_path):
    txt = ORDER.read_text(encoding="utf-8")
    changed = txt.replace("10.17129/botsci.1377", "10.17129/botsci.WRONG", 1)
    assert changed != txt
    path = tmp_path / "modified.csv"
    path.write_text(changed, encoding="utf-8")
    with pytest.raises(ValueError, match="Visitor-order source identity"):
        run(order=path)


def test_order_cannot_be_passed_as_new_coder_architecture(tmp_path):
    txt = ORDER.read_text(encoding="utf-8")
    assert ",NOT_OPENED," in txt
    path = tmp_path / "fabricated_outcome.csv"
    path.write_text(txt.replace(",NOT_OPENED,", ",STRUCTURAL_MODULE_DIVISION,", 1),
                    encoding="utf-8")
    with pytest.raises(ValueError, match="Cannot claim architecture observations"):
        run(order=path)


def test_source_timing_value_mutation_fails_closed(tmp_path):
    txt = U6_RECEIPTS.read_text(encoding="utf-8")
    old = ("Clusia_arrudae,conflict_timing_geometry,SEQUENTIAL_WITHIN_UNIT,")
    assert old in txt
    path = tmp_path / "altered_receipts.csv"
    path.write_text(txt.replace(
        old, "Clusia_arrudae,conflict_timing_geometry,SIMULTANEOUS,", 1
    ), encoding="utf-8")
    with pytest.raises(ValueError, match="Frozen source geometry"):
        run(u6_receipts=path)


def test_crosswalk_cannot_silently_drop_crescentia(tmp_path):
    rows = ORDER.read_text(encoding="utf-8").splitlines(keepends=True)
    altered = [r for r in rows if not r.startswith("Crescentia_alata,")]
    path = tmp_path / "subset.csv"
    path.write_text("".join(altered), encoding="utf-8")
    with pytest.raises(ValueError, match="Only three frozen"):
        run(order=path)


def test_no_fitted_effect_or_changed_admission_claimed():
    r = run()
    assert r["original_21_u6_admissions_changed"] is False
    assert r["source_predictor_values_modified"] is False
    assert r["architecture_outcomes_opened"] is False
    assert r["v4_model_fitted"] is False
    assert r["causal_study_contrast_estimated"] is False
