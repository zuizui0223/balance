from pathlib import Path

import csv
import json
import pytest

from balance_domain.monochoria_plastome_audit import (
    CORE_SINGLE_COPY_CDS,
    FIELDS,
    load_plastome_ledger,
    summarize_gene_support,
)


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "BALANCE_PLANT_U3_MONOCHORIA_PLASTOME_V1.csv"
RESULT = ROOT / "data" / "BALANCE_PLANT_U3_MONOCHORIA_PLASTOME_RESULT_V1.json"


def test_plastome_ledger_has_four_unique_complete_records():
    rows = load_plastome_ledger(LEDGER)
    by_taxon = {r["taxon"]: r for r in rows}
    assert by_taxon["Pontederia australasica"]["accession"] == "NC_063307.1"
    assert by_taxon["Pontederia cyanea"]["accession"] == "PQ010091.1"
    assert by_taxon["Pontederia korsakowii"]["accession"] == "PQ010093.1"
    assert by_taxon["Pontederia vaginalis"]["accession"] == "PQ010094.1"
    assert len({r["accession"] for r in rows}) == 4


def test_frozen_plastome_result_ranks_australasica_for_both_cases_without_species_tree_claim():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["shared_gene_count"] == 68
    assert result["concatenated_alignment_length"] == 51807
    assert result["candidate_pair_differences_on_shared_cds"] == 158
    for case in ("Pontederia korsakowii", "Pontederia vaginalis"):
        comparison = result["case_comparisons"][case]
        assert comparison["closest_candidate_by_p_distance"] == "Pontederia australasica"
        assert (
            comparison["candidate_distances"]["Pontederia australasica"]["p_distance"]
            < comparison["candidate_distances"]["Pontederia cyanea"]["p_distance"]
        )
    assert result["adjudication_use"] == "closest_control_candidate_ranking_tiebreak_only"
    assert "not_nuclear_species_tree" in result["claim_ceiling"]
    assert result["remaining_gate"].startswith(
        "direct_species_level_effective_animal_pollination"
    )


def test_core_gene_set_excludes_ir_and_trans_splicing_traps():
    assert "rps12" not in CORE_SINGLE_COPY_CDS
    assert "ndhB" not in CORE_SINGLE_COPY_CDS
    assert "ycf2" not in CORE_SINGLE_COPY_CDS
    assert "rbcL" in CORE_SINGLE_COPY_CDS
    assert "matK" in CORE_SINGLE_COPY_CDS


def test_gene_support_counts_candidate_wins_and_ties():
    genes = {
        "g1": {
            "Pontederia korsakowii": "AAAA",
            "Pontederia australasica": "AAAT",
            "Pontederia cyanea": "AATT",
        },
        "g2": {
            "Pontederia korsakowii": "CCCC",
            "Pontederia australasica": "CCCT",
            "Pontederia cyanea": "CCCT",
        },
        "g3": {
            "Pontederia korsakowii": "GGGG",
            "Pontederia australasica": "GGTT",
            "Pontederia cyanea": "GGGT",
        },
    }
    out = summarize_gene_support(genes, "Pontederia korsakowii")
    assert out["support_counts"] == {
        "Pontederia australasica": 1,
        "Pontederia cyanea": 1,
        "TIE": 1,
    }


def test_plastome_ledger_rejects_duplicate_accession(tmp_path):
    rows = load_plastome_ledger(LEDGER)
    rows[1]["accession"] = rows[0]["accession"]
    path = tmp_path / "ledger.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match="accession must be unique"):
        load_plastome_ledger(path)
