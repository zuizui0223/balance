from pathlib import Path

import pytest

from balance_domain.plant_u1 import (
    build_u1_handoff,
    load_u1_sample,
    load_u1_source_resolution,
)


ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = ROOT / "data" / "BALANCE_PLANT_U1_REVIEW_UNIVERSE_V1.csv"
SAMPLE = ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv"
RESOLUTION = ROOT / "data" / "BALANCE_PLANT_U1_SOURCE_RESOLUTION_V1.csv"


def test_u1_current_handoff_is_valid_but_not_frozen():
    readout = build_u1_handoff(UNIVERSE, SAMPLE, RESOLUTION)
    assert readout["review_reported_taxa"] == 47
    assert readout["registered_taxon_labels"] == 44
    assert readout["review_taxon_reconciliation_gap"] == 3
    assert readout["provisional_sample_size"] == 20
    assert readout["n_source_ready"] == 10
    assert readout["n_taxon_grain_conflicts"] == 2
    assert readout["double_code_sample_frozen"] is False


def test_u1_sample_retains_hard_cases_instead_of_replacing_them():
    rows = load_u1_sample(SAMPLE)
    taxa = [r["taxon_raw"] for r in rows]
    assert taxa[:5] == [
        "Aechmea pectinata",
        "Alstroemeria aurea",
        "Alstroemeria ligtu",
        "Alstroemeria ligtu var. Simsii",
        "Alstroemeria umbellata",
    ]
    assert "Berberis darwinii" in taxa
    assert "Brassica napus" in taxa
    assert "Cnidoscolus acontifolius" in taxa


def test_screen_ready_rows_require_clear_taxon_reconciliation():
    rows = load_u1_source_resolution(RESOLUTION)
    for row in rows:
        if row["screen_ready"] == "true":
            assert row["source_status"] == "RESOLVED_PRIMARY"
            assert row["primary_citation"]
            assert row["taxon_reconciliation"] == "CLEAR"


def test_ligtu_taxon_grain_conflict_blocks_both_labels():
    rows = load_u1_source_resolution(RESOLUTION)
    by_taxon = {r["taxon_raw"]: r for r in rows}
    assert by_taxon["Alstroemeria ligtu"]["screen_ready"] == "false"
    assert by_taxon["Alstroemeria ligtu var. Simsii"]["screen_ready"] == "false"
    assert by_taxon["Alstroemeria ligtu"]["doi"] == "10.1086/662029"
    assert by_taxon["Alstroemeria ligtu var. Simsii"]["doi"] == "10.1086/662029"
