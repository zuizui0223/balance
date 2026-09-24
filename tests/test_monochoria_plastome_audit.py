from pathlib import Path

import csv
import pytest

from balance_domain.monochoria_plastome_audit import (
    CORE_SINGLE_COPY_CDS,
    FIELDS,
    load_plastome_ledger,
    summarize_gene_support,
)


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "BALANCE_PLANT_U3_MONOCHORIA_PLASTOME_V1.csv"


def test_plastome_ledger_has_four_unique_complete_records():
    rows = load_plastome_ledger(LEDGER)
    by_taxon = {r["taxon"]: r for r in rows}
    assert by_taxon["Pontederia australasica"]["accession"] == "NC_063307.1"
    assert by_taxon["Pontederia cyanea"]["accession"] == "PQ010091.1"
    assert by_taxon["Pontederia korsakowii"]["accession"] == "PQ010093.1"
    assert by_taxon["Pontederia vaginalis"]["accession"] == "PQ010094.1"
    assert len({r["accession"] for r in rows}) == 4


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
