from pathlib import Path

from balance_domain.plant_universe_union import (
    FROZEN_FRAME_STATUS,
    build_cross_universe_readout,
    load_cross_universe_map,
)

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "data" / "BALANCE_PLANT_CROSS_UNIVERSE_DEPENDENCY_MAP_V1.csv"

def test_cross_universe_map_deduplicates_full47_and_u2_groups():
    rows = load_cross_universe_map(MAP)
    assert len(rows) == 67
    assert len({r["dependency_group"] for r in rows}) == 67
    assert all(r["union_frame_status"] == FROZEN_FRAME_STATUS for r in rows)

def test_cross_universe_map_keeps_review_membership_without_double_counting():
    readout = build_cross_universe_readout(MAP)
    assert readout["membership_counts"] == {"U1": 45, "U1;U2": 2, "U2": 20}
    assert readout["n_multi_universe_overlap_groups"] == 2
    assert readout["multi_universe_overlap_groups"] == [
        "Ipomopsis_aggregata",
        "Mimulus_aurantiacus",
    ]

def test_u1_direct_supplement_taxa_enter_frozen_union_once():
    rows = {r["dependency_group"]: r for r in load_cross_universe_map(MAP)}
    for dep, record_id in {
        "Eichhornia_crassipes": "U1_045",
        "Nemophila_menziesii": "U1_046",
        "Ruellia_nudiflora": "U1_047",
    }.items():
        row = rows[dep]
        assert row["universe_membership"] == "U1"
        assert row["u1_record_id"] == record_id
        assert row["overlap_status"] == "SINGLE_UNIVERSE"

def test_overlap_rows_keep_both_review_record_ids():
    rows = {r["dependency_group"]: r for r in load_cross_universe_map(MAP)}
    for dep in ("Ipomopsis_aggregata", "Mimulus_aurantiacus"):
        row = rows[dep]
        assert row["universe_membership"] == "U1;U2"
        assert row["u1_record_id"].startswith("U1_")
        assert row["u2_record_id"].startswith("U2_")
        assert row["overlap_status"] == "MULTI_UNIVERSE_SAME_DEPENDENCY_GROUP"

def test_union_claim_ceiling_rejects_bibliographic_replication_as_biology():
    readout = build_cross_universe_readout(MAP)
    assert "not_independent_replication" in readout["claim_ceiling"]
    assert "source_closed" in readout["claim_ceiling"]
