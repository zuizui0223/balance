from pathlib import Path

import csv
import pytest

from balance_domain.plant_u1_production_sources import (
    FIELDS,
    build_u1_production_source_readout,
    load_u1_production_source_map,
)


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "data" / "BALANCE_PLANT_U1_PRODUCTION_SOURCE_MAP_V1.csv"
UNIVERSE = ROOT / "data" / "BALANCE_PLANT_U1_REVIEW_UNIVERSE_V1.csv"


def test_u1_remaining_27_primary_study_identities_are_mapped():
    rows = load_u1_production_source_map(MAP, UNIVERSE)
    out = build_u1_production_source_readout(MAP, UNIVERSE)
    assert len(rows) == 27
    assert out["n_mapped_taxa"] == 27
    assert out["all_source_identities_mapped"] is True
    assert out["n_source_ready_primary"] == 0
    assert out["n_content_retrieval_pending"] == 27
    assert out["all_source_content_ready"] is False


def test_multi_study_u1_taxa_are_explicit():
    out = build_u1_production_source_readout(MAP, UNIVERSE)
    assert out["multi_study_taxa"] == [
        "Isomeris arborea",
        "Pastinaca sativa",
        "Verbascum nigrum",
    ]


def test_direct_figshare_article_ids_are_frozen_for_supplement_taxa():
    rows = {r["taxon_raw"]: r for r in load_u1_production_source_map(MAP, UNIVERSE)}
    assert rows["Eichhornia crassipes"]["figshare_article_ids"] == "294"
    assert rows["Nemophila menziesii"]["figshare_article_ids"] == "1079"
    assert rows["Ruellia nudiflora"]["figshare_article_ids"] == "1143"


def test_pending_content_cannot_claim_resolved_primary_in_universe(tmp_path):
    with MAP.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows[0]["source_content_status"] = "SOURCE_READY_PRIMARY"
    path = tmp_path / "map.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match="universe source status disagrees"):
        load_u1_production_source_map(path, UNIVERSE)
