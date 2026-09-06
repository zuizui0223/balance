import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "comparative" / "GENERALITY_CANDIDATE_MATRIX_V1.csv"


def _rows():
    with MATRIX.open(encoding="utf-8", newline="") as handle:
        return {row["system"]: row for row in csv.DictReader(handle)}


def test_pedicularis_is_primary_but_not_empirically_promoted() -> None:
    row = _rows()["Pedicularis_rex"]
    assert row["replication_priority"] == "G0_FIRST"
    assert "NOT_EXECUTED" in row["SCH_status"]
    assert "NOT_EXECUTED" in row["BALANCE_status"]
    assert "NOT_EXECUTED" in row["BITA_status"]


def test_negative_controls_are_explicit() -> None:
    rows = _rows()
    assert "NEGATIVE" in rows["Ipomopsis_aggregata"]["causal_level"]
    assert "ALIGNED_OPTIMUM_NEGATIVE_CONTROL" == rows["Platycodon_grandiflorus"]["SCH_status"]
    assert "EXPECTED_NO_SCH_CONFLICT" in rows["Platycodon_grandiflorus"]["BALANCE_status"]


def test_unreviewed_cross_chapter_cells_remain_unreviewed() -> None:
    rows = _rows()
    assert rows["Dalechampia_spp"]["BALANCE_status"] == "NOT_YET_AUDITED"
    assert rows["Castilleja_linariaefolia"]["BITA_status"] == "NOT_YET_AUDITED"
    assert rows["Polemonium_viscosum"]["BALANCE_status"] == "NOT_YET_AUDITED"
    assert rows["Cichlid_oral_pharyngeal_jaws"]["SCH_status"] == "NOT_YET_AUDITED"


def test_observational_anchors_are_not_relabeled_as_causal_three_world_proofs() -> None:
    rows = _rows()
    peucedanum = rows["Peucedanum_multivittatum"]
    dalechampia = rows["Dalechampia_spp"]
    cichlid = rows["Cichlid_oral_pharyngeal_jaws"]
    assert "NO_DIRECT_WORLDLINE" in peucedanum["BALANCE_status"]
    assert "D2_NOT_IDENTIFIED" in peucedanum["BITA_status"]
    assert "HISTORICAL" in dalechampia["BITA_status"]
    assert "ANCHOR" in cichlid["BITA_status"]
