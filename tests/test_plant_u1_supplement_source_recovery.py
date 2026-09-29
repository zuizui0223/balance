from pathlib import Path

import csv
import json


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "data" / "BALANCE_PLANT_U1_SUPPLEMENT_SOURCE_RECOVERY_V1.json"
CANDIDATES = ROOT / "data" / "BALANCE_PLANT_U1_SUPPLEMENT_TAXON_CANDIDATES_V1.csv"
UNIVERSE = ROOT / "data" / "BALANCE_PLANT_U1_REVIEW_UNIVERSE_V1.csv"


def test_u1_figshare_source_closes_full47_reconciliation():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["reported_plant_taxa"] == 47
    assert receipt["current_network_visible_taxa"] == 44
    assert receipt["reconciliation_gap"] == 0
    assert receipt["figshare_dataset"]["doi"] == "10.6084/m9.figshare.12397772.v1"
    assert receipt["figshare_dataset"]["status"] == "INGESTED_AND_RECONCILED"
    assert receipt["canonical_universe_status"] == "SOURCE_CLOSED_FULL47"
    assert receipt["recovered_supplement_only_taxa"] == [
        "Eichhornia crassipes",
        "Nemophila menziesii",
        "Ruellia nudiflora",
    ]
    assert "not_prevalence" in receipt["claim_ceiling"]


def test_u1_candidate_registry_records_direct_confirmations_and_exclusions():
    with CANDIDATES.open(encoding="utf-8", newline="") as handle:
        candidates = {row["taxon_raw"]: row for row in csv.DictReader(handle)}

    for taxon in ("Nemophila menziesii", "Eichhornia crassipes", "Ruellia nudiflora"):
        assert candidates[taxon]["confidence"] == "CONFIRMED"
        assert candidates[taxon]["reconciliation_status"] == (
            "DIRECT_FIGSHARE_CONFIRMED_SUPPLEMENT_ONLY"
        )

    for taxon in (
        "Alstroemeria exerens",
        "Cucurbita pepo ssp. texana",
        "Mimulus luteus",
        "Mimulus guttatus",
    ):
        assert candidates[taxon]["confidence"] == "EXCLUDED"
        assert candidates[taxon]["reconciliation_status"] == (
            "DIRECT_FIGSHARE_RECONCILIATION_EXCLUDED"
        )


def test_u1_directly_confirmed_taxa_enter_canonical_universe_and_false_candidate_does_not():
    with UNIVERSE.open(encoding="utf-8", newline="") as handle:
        universe_taxa = {row["taxon_raw"] for row in csv.DictReader(handle)}

    assert {"Nemophila menziesii", "Eichhornia crassipes", "Ruellia nudiflora"} <= universe_taxa
    assert "Alstroemeria exerens" not in universe_taxa
