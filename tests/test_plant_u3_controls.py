import csv
from pathlib import Path

import pytest

from balance_domain.plant_u3_controls import FIELDS, build_u3_matched_control_readout, load_u3_matched_controls


ROOT = Path(__file__).resolve().parents[1]
U3 = ROOT / "data" / "BALANCE_PLANT_U3_HETERANTHERY_REVIEW_UNIVERSE_V1.csv"
CASES = ROOT / "data" / "BALANCE_PLANT_U3_CASE_CANDIDATES_V1.csv"


def _row(**updates):
    row = {
        "pair_id": "p1",
        "pair_role": "PRIMARY",
        "case_family": "Solanaceae",
        "case_taxon": "Solanum rostratum",
        "case_source_id": "Vallejo-Marin_Manson_Thomson_Barrett_2009_JEB",
        "control_taxon": "Solanum controlense",
        "control_source_id": "control_source",
        "match_level": "CONGENERIC",
        "phylogenetic_basis": "frozen_phylogeny",
        "animal_pollination_eligible": "true",
        "heteranthery_absence_confirmed": "true",
        "selection_status": "ADJUDICATED",
        "tie_break_used": "NONE",
        "predictor_blinding_status": "BLINDED",
        "notes": "",
    }
    row.update(updates)
    return row


def _write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_adjudicated_primary_control_can_pass(tmp_path):
    path = tmp_path / "pairs.csv"
    _write(path, [_row()])
    rows = load_u3_matched_controls(path, CASES, U3)
    assert rows[0]["case_taxon"] == "Solanum rostratum"


def test_primary_control_is_unique_per_case(tmp_path):
    path = tmp_path / "pairs.csv"
    _write(path, [_row(), _row(pair_id="p2", control_taxon="Solanum secondense")])
    with pytest.raises(ValueError, match="more than one PRIMARY control"):
        load_u3_matched_controls(path, CASES, U3)


def test_adjudicated_control_must_be_predictor_blinded(tmp_path):
    path = tmp_path / "pairs.csv"
    _write(path, [_row(predictor_blinding_status="UNBLINDED")])
    with pytest.raises(ValueError, match="selected before predictor extraction"):
        load_u3_matched_controls(path, CASES, U3)


def test_screened_pair_can_remain_unresolved(tmp_path):
    path = tmp_path / "pairs.csv"
    _write(
        path,
        [
            _row(
                selection_status="SCREENED",
                animal_pollination_eligible="false",
                heteranthery_absence_confirmed="false",
                predictor_blinding_status="UNCERTAIN",
            )
        ],
    )
    rows = load_u3_matched_controls(path, CASES, U3)
    assert rows[0]["selection_status"] == "SCREENED"


def test_readout_stays_open_until_all_registered_cases_have_primary_controls(tmp_path):
    path = tmp_path / "pairs.csv"
    _write(path, [_row()])
    readout = build_u3_matched_control_readout(path, CASES, U3)
    assert readout["n_adjudicated_primary_pairs"] == 1
    assert readout["n_registered_case_taxa"] == 6
    assert readout["case_control_layer_closed"] is False
    assert "Solanum rostratum" not in readout["unmatched_case_taxa"]
