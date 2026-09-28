import csv
from pathlib import Path

import pytest

from balance_domain.plant_u6 import (
    FIELDS,
    FORBIDDEN_PASS1_FIELDS,
    load_u6_anchor,
    load_u6_reference_classification,
)


ROOT = Path(__file__).resolve().parents[1]
ANCHOR = ROOT / "data" / "BALANCE_PLANT_U6_REVIEW_ANCHOR_V1.json"
TEMPLATE = ROOT / "data" / "BALANCE_PLANT_U6_REFERENCE_CLASSIFICATION_TEMPLATE_V1.csv"


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
