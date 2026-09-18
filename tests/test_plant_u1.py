from pathlib import Path

from balance_domain.plant_u1 import (
    build_u1_handoff,
    load_u1_sample,
    load_u1_source_resolution,
    load_u1_universe,
)


ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = ROOT / "data" / "BALANCE_PLANT_U1_REVIEW_UNIVERSE_V1.csv"
SAMPLE = ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv"
RESOLUTION = ROOT / "data" / "BALANCE_PLANT_U1_SOURCE_RESOLUTION_V1.csv"


def test_u1_current_handoff_is_valid_but_not_frozen():
    readout = build_u1_handoff(UNIVERSE, SAMPLE, RESOLUTION)
    assert readout["review_reported_taxa"] == 47
    assert readout["network_visible_taxon_labels"] == 44
    assert readout["network_visible_expected_labels"] == 44
    assert readout["supplement_only_taxa_to_recover"] == 3
    assert readout["provisional_sample_size"] == 20
    assert readout["n_source_ready"] == 17
    assert readout["n_taxon_grain_conflicts"] == 0
    assert readout["double_code_sample_frozen"] is False


def test_u1_sample_retains_hard_cases_instead_of_replacing_them():
    rows = load_u1_sample(SAMPLE)
    taxa = [r["taxon_raw"] for r in rows]
    assert taxa[:5] == [
        "Aechmea pectinata",
        "Alstroemeria aurea",
        "Alstroemeria ligtu var. Simsii",
        "Alstroemeria umbellata",
        "Aristotelia chilensis",
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


def test_five_newly_resolved_sources_are_screen_ready():
    rows = load_u1_source_resolution(RESOLUTION)
    by_taxon = {r["taxon_raw"]: r for r in rows}
    for taxon in (
        "Aristotelia chilensis",
        "Berberis darwinii",
        "Bouvardia ternifolia",
        "Cardus thoermeri",
        "Cnidoscolus acontifolius",
    ):
        assert by_taxon[taxon]["screen_ready"] == "true"
        assert by_taxon[taxon]["source_status"] == "RESOLVED_PRIMARY"


def test_corrected_network_sample_contains_one_ligtu_var_and_adds_cynanchum():
    rows = load_u1_source_resolution(RESOLUTION)
    taxa = [r["taxon_raw"] for r in rows]
    assert "Alstroemeria ligtu" not in taxa
    assert taxa.count("Alstroemeria ligtu var. Simsii") == 1
    assert "Cynanchum diemii" in taxa
    by_taxon = {r["taxon_raw"]: r for r in rows}
    assert by_taxon["Alstroemeria ligtu var. Simsii"]["screen_ready"] == "true"
    assert by_taxon["Alstroemeria ligtu var. Simsii"]["doi"] == "10.1086/662029"
    assert by_taxon["Cynanchum diemii"]["screen_ready"] == "true"
    assert by_taxon["Cynanchum diemii"]["doi"] == "10.1890/02-4055"


def test_u1_universe_and_resolution_source_statuses_are_synchronized():
    universe = {r["universe_record_id"]: r for r in load_u1_universe(UNIVERSE)}
    resolution = load_u1_source_resolution(RESOLUTION)
    for row in resolution:
        assert universe[row["universe_record_id"]]["primary_source_status"] == row["source_status"]
