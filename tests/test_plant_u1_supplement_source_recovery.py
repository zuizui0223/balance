from pathlib import Path

import csv
import json


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "data" / "BALANCE_PLANT_U1_SUPPLEMENT_SOURCE_RECOVERY_V1.json"
CANDIDATES = ROOT / "data" / "BALANCE_PLANT_U1_SUPPLEMENT_TAXON_CANDIDATES_V1.csv"
UNIVERSE = ROOT / "data" / "BALANCE_PLANT_U1_REVIEW_UNIVERSE_V1.csv"


def test_u1_supplement_source_surfaces_are_located_but_not_promoted():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["reported_plant_taxa"] == 47
    assert receipt["current_network_visible_taxa"] == 44
    assert receipt["reconciliation_gap"] == 3
    assert receipt["supplemental_information_1"]["doi"] == "10.7717/peerj.9049/supp-1"
    assert receipt["supplemental_information_2"]["doi"] == "10.7717/peerj.9049/supp-2"
    assert receipt["figshare_dataset"]["doi"] == "10.6084/m9.figshare.12397772.v1"
    assert receipt["supplemental_information_1"]["status"] == "LOCATED_NOT_INGESTED"
    assert receipt["supplemental_information_2"]["status"] == "LOCATED_NOT_INGESTED"
    assert receipt["figshare_dataset"]["status"] == "LOCATED_NOT_INGESTED"
    assert receipt["canonical_universe_status"] == "OPEN"
    assert receipt["candidate_registry_status"] == "PROVISIONAL_ONLY"
    assert "not_taxon_promotion" in receipt["claim_ceiling"]


def test_u1_candidate_confidence_matches_canonical_registry():
    with CANDIDATES.open(encoding="utf-8", newline="") as handle:
        candidates = {row["taxon_raw"]: row for row in csv.DictReader(handle)}

    assert candidates["Cucurbita pepo ssp. texana"]["confidence"] == "MEDIUM"
    for taxon in (
        "Nemophila menziesii",
        "Eichhornia crassipes",
        "Alstroemeria exerens",
    ):
        assert candidates[taxon]["confidence"] == "VERY_HIGH"


def test_u1_high_confidence_candidates_are_not_silently_in_canonical_universe():
    with UNIVERSE.open(encoding="utf-8", newline="") as handle:
        universe_taxa = {row["taxon_raw"] for row in csv.DictReader(handle)}

    assert {
        "Nemophila menziesii",
        "Eichhornia crassipes",
        "Alstroemeria exerens",
    }.isdisjoint(universe_taxa)
