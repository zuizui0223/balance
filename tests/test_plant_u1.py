from pathlib import Path

from balance_domain.plant_u1 import (
    FROZEN_DOUBLE_CODE_STATUS,
    FROZEN_SELECTION_RULE,
    build_u1_handoff,
    load_u1_sample,
    load_u1_source_resolution,
    load_u1_universe,
)

ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = ROOT / "data" / "BALANCE_PLANT_U1_REVIEW_UNIVERSE_V1.csv"
SAMPLE = ROOT / "data" / "BALANCE_PLANT_U1_DOUBLE_CODE_SAMPLE_V1.csv"
RESOLUTION = ROOT / "data" / "BALANCE_PLANT_U1_SOURCE_RESOLUTION_V1.csv"

def test_u1_full47_handoff_is_source_closed_and_sample_frozen():
    readout = build_u1_handoff(UNIVERSE, SAMPLE, RESOLUTION)
    assert readout["review_reported_taxa"] == 47
    assert readout["full_review_registered_taxa"] == 47
    assert readout["network_visible_taxon_labels"] == 44
    assert readout["supplement_only_taxa_recovered"] == 3
    assert readout["supplement_only_taxa_to_recover"] == 0
    assert readout["n_source_ready"] == 20
    assert readout["n_taxon_grain_conflicts"] == 0
    assert readout["double_code_sample_frozen"] is True

def test_direct_figshare_reconciliation_adds_exactly_three_supplement_taxa():
    rows = load_u1_universe(UNIVERSE)
    supplement = {r["taxon_raw"] for r in rows if r["source_surface"] == "FIGSHARE_ANALYSIS_LIST_SUPPLEMENT_ONLY_TAXON"}
    assert supplement == {"Eichhornia crassipes", "Nemophila menziesii", "Ruellia nudiflora"}

def test_u1_sample_is_unchanged_after_full47_reconciliation():
    rows = load_u1_sample(SAMPLE)
    assert [r["taxon_raw"] for r in rows][-4:] == ["Cucumis melo", "Cucumis sativus", "Cucurbita moschata", "Cynanchum diemii"]
    assert all(r["selection_rule"] == FROZEN_SELECTION_RULE for r in rows)
    assert all(r["double_code_status"] == FROZEN_DOUBLE_CODE_STATUS for r in rows)

def test_all_frozen_first20_sources_are_ready():
    rows = load_u1_source_resolution(RESOLUTION)
    assert len(rows) == 20
    assert all(r["screen_ready"] == "true" for r in rows)
    assert all(r["source_status"] == "RESOLVED_PRIMARY" for r in rows)
