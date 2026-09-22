from pathlib import Path

import csv
import pytest

from balance_domain.plant_u3_adjudication import (
    FIELDS,
    build_u3_control_adjudication_readout,
    load_u3_control_adjudication,
)


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"
PAIRS = ROOT / "data" / "BALANCE_PLANT_U3_MATCHED_CONTROLS_V1.csv"
ADJ = ROOT / "data" / "BALANCE_PLANT_U3_CONTROL_ADJUDICATION_V1.csv"


def test_real_u3_adjudication_has_two_pass_four_open():
    rows = load_u3_control_adjudication(ADJ, PAIRS, CASES, U3)
    assert len(rows) == 6
    readout = build_u3_control_adjudication_readout(ADJ, PAIRS, CASES, U3)
    assert readout["decision_counts"] == {"OPEN": 4, "PASS": 2}
    assert set(readout["open_pair_ids"]) == {
        "U3_PAIR_MONKO_001",
        "U3_PAIR_MONVA_001",
        "U3_PAIR_SENAL_001",
        "U3_PAIR_SENBI_001",
    }
    assert readout["adjudication_closed"] is False


def test_pass_rows_match_adjudicated_pair_registry():
    rows = load_u3_control_adjudication(ADJ, PAIRS, CASES, U3)
    passed = {r["case_taxon"] for r in rows if r["decision"] == "PASS"}
    assert passed == {"Solanum rostratum", "Melastoma malabathricum"}


def _read_rows():
    with ADJ.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_pass_cannot_hide_open_gate(tmp_path):
    rows = _read_rows()
    rows[0]["animal_pollination_status"] = "OPEN"
    path = tmp_path / "adj.csv"
    _write(path, rows)
    with pytest.raises(ValueError, match="PASS decision requires all gates PASS"):
        load_u3_control_adjudication(path, PAIRS, CASES, U3)


def test_open_requires_explicit_blocker(tmp_path):
    rows = _read_rows()
    target = next(r for r in rows if r["decision"] == "OPEN")
    target["blocker"] = ""
    path = tmp_path / "adj.csv"
    _write(path, rows)
    with pytest.raises(ValueError, match="OPEN decision requires an explicit blocker"):
        load_u3_control_adjudication(path, PAIRS, CASES, U3)


def test_decision_must_match_pair_selection_status(tmp_path):
    rows = _read_rows()
    target = next(r for r in rows if r["decision"] == "OPEN")
    for field in (
        "phylogenetic_proximity_status",
        "heteranthery_absence_status",
        "animal_pollination_status",
        "closer_eligible_alternative_search",
        "tie_break_status",
        "predictor_blinding_status",
    ):
        target[field] = "PASS"
    target["decision"] = "PASS"
    target["blocker"] = ""
    path = tmp_path / "adj.csv"
    _write(path, rows)
    with pytest.raises(ValueError, match="pair registry ADJUDICATED"):
        load_u3_control_adjudication(path, PAIRS, CASES, U3)
