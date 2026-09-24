from pathlib import Path

from balance_domain.plant_u3_dependence import (
    RULE,
    build_u3_dependence_readout,
    load_u3_dependence,
)

ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
PAIRS = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv"
ADJ = ROOT / "data" / "BALANCE_PLANT_U3_CONTROL_ADJUDICATION_V1.csv"
DEPEND = ROOT / "data" / "BALANCE_PLANT_U3_DEPENDENCE_V1.csv"


def test_u3_dependence_covers_six_pairs_in_four_blocks():
    rows = load_u3_dependence(DEPEND, ADJ, PAIRS, CASES, U3)
    assert len(rows) == 6
    assert len({r["dependence_block_id"] for r in rows}) == 4
    assert all(r["dependence_rule"] == RULE for r in rows)


def test_current_four_pass_pairs_reduce_to_three_dependence_blocks():
    out = build_u3_dependence_readout(DEPEND, ADJ, PAIRS, CASES, U3)
    assert out["n_pass_pairs"] == 4
    assert out["n_pass_dependence_blocks"] == 3
    assert out["pass_dependence_blocks"] == [
        "U3_DEP_MELASTOMATEAE_01",
        "U3_DEP_SENNA_01",
        "U3_DEP_SOLANUM_01",
    ]
    assert out["naive_pair_independence_allowed"] is False
    assert out["dependence_specification_frozen"] is True


def test_monochoria_shared_control_is_one_dependence_block():
    rows = load_u3_dependence(DEPEND, ADJ, PAIRS, CASES, U3)
    mono = [r for r in rows if r["dependence_block_id"] == "U3_DEP_MONOCHORIA_01"]
    assert len(mono) == 2
    assert {r["control_taxon"] for r in mono} == {"Monochoria australasica"}
    assert {r["adjudication_state"] for r in mono} == {"OPEN"}
    assert all(r["control_reuse_status"] == "REUSED_CONTROL_TWO_PAIRS" for r in mono)

    out = build_u3_dependence_readout(DEPEND, ADJ, PAIRS, CASES, U3)
    assert out["n_reused_controls"] == 1
    assert out["reused_controls"] == ["Monochoria australasica"]


def test_senna_pairs_are_not_two_independent_deep_origins():
    rows = load_u3_dependence(DEPEND, ADJ, PAIRS, CASES, U3)
    senna = [r for r in rows if r["dependence_block_id"] == "U3_DEP_SENNA_01"]
    assert len(senna) == 2
    assert {r["case_taxon"] for r in senna} == {"Senna alata", "Senna bicapsularis"}
    assert {r["adjudication_state"] for r in senna} == {"PASS"}
