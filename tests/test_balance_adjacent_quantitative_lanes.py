import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANES = ROOT / "data" / "BALANCE_ADJACENT_QUANTITATIVE_LANES_V1.csv"


def _rows():
    with LANES.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_adjacent_lanes_are_not_backfilled_into_strict_q1b():
    rows = _rows()
    assert len(rows) == 5
    assert all(row["pooling_eligibility"] != "STRICT_Q1B_POSITIVE" for row in rows)
    assert {row["system_taxon"] for row in rows} == {
        "Ipomopsis species and hybrids",
        "Primula farinosa",
        "Trifolium repens",
        "Lythrum salicaria",
        "Gymnadenia conopsea",
    }


def test_negative_controls_remain_negative_controls():
    rows = {row["lane_id"]: row for row in _rows()}
    assert rows["NEGATIVE_TRIFOLIUM_2018"]["pooling_eligibility"] == "NEGATIVE_CONTROL_ONLY"
    assert rows["NEGATIVE_LYTHRUM_2017"]["pooling_eligibility"] == "NEGATIVE_CONTROL_ONLY"
    assert rows["NEGATIVE_LYTHRUM_2017"]["effect_status"] == "NEGATIVE_CONTROL_EFFECT_READY"
    assert "inevitable-conflict" in rows["NEGATIVE_LYTHRUM_2017"]["claim_ceiling"]


def test_sequential_and_discrete_estimands_stay_separate():
    rows = {row["lane_id"]: row for row in _rows()}
    assert rows["SEQUENTIAL_IPOMOPSIS_2022"]["pooling_eligibility"] == "SEPARATE_LANE_NOT_Q1B"
    assert rows["DISCRETE_PRIMULA_FARINOSA_2013"]["pooling_eligibility"] == "SEPARATE_LANE_NOT_Q1B"
    assert "do not convert to continuous beta" in rows["DISCRETE_PRIMULA_FARINOSA_2013"]["claim_ceiling"]


def test_antagonist_attribution_failure_is_preserved():
    rows = {row["lane_id"]: row for row in _rows()}
    residual = rows["RESIDUAL_GYMNADENIA_2019"]
    assert residual["effect_status"] == "ANTAGONIST_IDENTITY_FAIL"
    assert residual["pooling_eligibility"] == "SEPARATE_UNRESOLVED_LANE"
