import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READOUT = ROOT / "data" / "BALANCE_REALITY_BOUNDARY_READOUT_V1.csv"


def _rows():
    with READOUT.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_strict_q1b_positive_numerator_remains_three():
    rows = _rows()
    positives = [r for r in rows if r["layer"] == "STRICT_POSITIVE"]
    assert len(positives) == 3
    assert {r["system_taxon"] for r in positives} == {
        "Fragaria vesca",
        "Impatiens capensis",
        "Gymnadenia conopsea",
    }
    assert all(r["enters_strict_q1b_pool"] == "yes" for r in positives)


def test_negative_boundary_and_attribution_layers_stay_outside_pool():
    rows = _rows()
    nonpositives = [r for r in rows if r["layer"] != "STRICT_POSITIVE"]
    assert all(r["enters_strict_q1b_pool"] == "no" for r in nonpositives)
    assert {r["layer"] for r in nonpositives} == {
        "NEGATIVE_CONTROL",
        "BOUNDARY",
        "ATTRIBUTION_FAIL",
    }


def test_negative_controls_are_retained_as_inference_not_failures():
    rows = _rows()
    negatives = [r for r in rows if r["layer"] == "NEGATIVE_CONTROL"]
    assert {r["system_taxon"] for r in negatives} == {
        "Trifolium repens",
        "Lythrum salicaria",
    }
    assert any("not inevitably" in r["interpretation"] for r in negatives)


def test_statistical_opposition_without_antagonist_identity_is_not_promoted():
    rows = _rows()
    attribution = [r for r in rows if r["layer"] == "ATTRIBUTION_FAIL"]
    assert len(attribution) == 1
    assert attribution[0]["enters_strict_q1b_pool"] == "no"
    assert "insufficient" in attribution[0]["interpretation"]
