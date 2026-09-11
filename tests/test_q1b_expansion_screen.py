import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCREEN = ROOT / "data" / "BALANCE_Q1B_EXPANSION_SCREEN_V1.csv"
STRATA = ROOT / "data" / "BALANCE_QUANTITATIVE_STRATA_V1.csv"


def _rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_strict_q1b_pool_remains_three_until_new_compatible_positive_exists():
    strata = {r["stratum_id"]: r for r in _rows(STRATA)}
    q1b = strata["DIFFUSE_FACTORIAL_AGENT_SELECTION"]
    assert q1b["effect_size_ready_clusters"] == "3"
    assert q1b["registered_pattern_candidates"] == "3"
    assert q1b["pooling_status"] == "POOLING_OPEN_FIRST_THREE_CLUSTER_POOL_FROZEN"


def test_sequential_filter_ipomopsis_is_not_backfilled_into_factorial_q1b():
    rows = {r["candidate_id"]: r for r in _rows(SCREEN)}
    row = rows["CAMPBELL_IPOMOPSIS_2022"]
    assert row["current_decision"] == "EXCLUDE_FROM_STRICT_Q1B"
    assert row["next_lane"] == "SEQUENTIAL_FILTER_QUANTITATIVE_LANE"


def test_design_matched_negative_controls_stay_out_of_positive_numerator():
    rows = {r["candidate_id"]: r for r in _rows(SCREEN)}
    assert rows["SANTANGELO_TRIFOLIUM_2018"]["current_decision"] == "NEGATIVE_CONTROL"
    assert rows["THOMSEN_LYTHRUM_2017"]["current_decision"] == "NEGATIVE_CONTROL"


def test_discrete_morph_and_nonantagonist_contexts_are_separate_estimands():
    rows = {r["candidate_id"]: r for r in _rows(SCREEN)}
    assert rows["AGREN_PRIMULA_2013"]["next_lane"] == "DISCRETE_MORPH_AGENT_SELECTION"
    assert rows["SLETVOLD_DACTYLORHIZA_2017"]["current_decision"] == "EXCLUDE_AGENT_CLASS"
