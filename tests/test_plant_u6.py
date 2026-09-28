import csv
from pathlib import Path

import pytest

from balance_domain.plant_u6 import (
    FIELDS,
    FORBIDDEN_PASS1_FIELDS,
    build_u6_multi_batch_readout,
    build_u6_reference_readout,
    load_u6_anchor,
    load_u6_reference_classification,
)


ROOT = Path(__file__).resolve().parents[1]
ANCHOR = ROOT / "data" / "BALANCE_PLANT_U6_REVIEW_ANCHOR_V1.json"
TEMPLATE = ROOT / "data" / "BALANCE_PLANT_U6_REFERENCE_CLASSIFICATION_TEMPLATE_V1.csv"
BATCH_A = ROOT / "data" / "BALANCE_PLANT_U6_REFERENCE_CLASSIFICATION_BATCH_A_V1.csv"
BATCH_B = ROOT / "data" / "BALANCE_PLANT_U6_REFERENCE_CLASSIFICATION_BATCH_B_V1.csv"


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



def test_u6_batch_a_freezes_first_34_references_without_inclusion():
    rows = load_u6_reference_classification(BATCH_A)
    assert len(rows) == 34
    assert [row["reference_id"] for row in rows] == [
        f"U6_REF_{i:03d}" for i in range(1, 35)
    ]
    with BATCH_A.open(encoding="utf-8", newline="") as handle:
        fields = set(csv.DictReader(handle).fieldnames or ())
    assert fields.isdisjoint(FORBIDDEN_PASS1_FIELDS)

    out = build_u6_reference_readout(BATCH_A)
    assert out["pollen_theft_candidate_reference_ids"] == [
        "U6_REF_010",
        "U6_REF_017",
        "U6_REF_029",
        "U6_REF_031",
        "U6_REF_033",
    ]
    assert out["n_included"] == 0
    assert out["architecture_fields_open"] is False
    assert out["pass2_open"] is False



def test_u6_batch_b_continues_reference_order_without_architecture_fields():
    rows = load_u6_reference_classification(BATCH_B)
    assert len(rows) == 33
    assert [row["reference_id"] for row in rows] == [
        f"U6_REF_{i:03d}" for i in range(35, 68)
    ]
    with BATCH_B.open(encoding="utf-8", newline="") as handle:
        fields = set(csv.DictReader(handle).fieldnames or ())
    assert fields.isdisjoint(FORBIDDEN_PASS1_FIELDS)

    out = build_u6_reference_readout(BATCH_B)
    assert out["pollen_theft_candidate_reference_ids"] == [
        "U6_REF_046",
        "U6_REF_058",
    ]
    assert out["n_included"] == 0


def test_u6_batches_a_b_form_one_consecutive_blinded_reconstruction():
    out = build_u6_multi_batch_readout([BATCH_A, BATCH_B])
    assert out["n_references"] == 67
    assert out["first_reference_id"] == "U6_REF_001"
    assert out["last_reference_id"] == "U6_REF_067"
    assert out["pollen_theft_candidate_reference_ids"] == [
        "U6_REF_010",
        "U6_REF_017",
        "U6_REF_029",
        "U6_REF_031",
        "U6_REF_033",
        "U6_REF_046",
        "U6_REF_058",
    ]
    assert out["n_candidates"] == 7
    assert out["n_included"] == 0
    assert out["architecture_fields_open"] is False
    assert out["pass2_open"] is False
