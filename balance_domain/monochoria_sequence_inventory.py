"""NCBI nucleotide inventory for the unresolved U3 Pontederia cyanea surface."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


CURRENT_MARKERS = {"ndhf", "rbcl"}


def classify_record(description: str, length: int, genes: list[str]) -> str:
    desc = description.casefold()
    normalized = {gene.casefold() for gene in genes}
    if length >= 100_000 and ("chloroplast" in desc or "plast" in desc):
        return "COMPLETE_PLASTOME"
    additional = normalized - CURRENT_MARKERS
    if additional:
        return "ADDITIONAL_ANNOTATED_LOCUS"
    if normalized & CURRENT_MARKERS:
        return "CURRENT_MARKER_ONLY"
    if length >= 5_000:
        return "OTHER_LONG_RECORD"
    return "OTHER_SHORT_RECORD"


def _fetch_records_for_taxid(taxid: int):
    from Bio import Entrez, SeqIO

    Entrez.email = "balance-sequence-inventory@users.noreply.github.com"
    with Entrez.esearch(
        db="nuccore",
        term=f"txid{taxid}[Organism:noexp]",
        retmax=500,
    ) as handle:
        search = Entrez.read(handle)
    ids = list(search.get("IdList", []))
    count = int(search.get("Count", 0))
    if count != len(ids):
        raise ValueError(
            f"taxid {taxid} returned {count} records but only {len(ids)} IDs; raise retmax"
        )
    if not ids:
        return []

    records = []
    for start in range(0, len(ids), 50):
        chunk = ids[start : start + 50]
        with Entrez.efetch(
            db="nuccore",
            id=",".join(chunk),
            rettype="gbwithparts",
            retmode="text",
        ) as handle:
            records.extend(SeqIO.parse(handle, "genbank"))
        time.sleep(0.4)
    return records


def summarize_taxon(label: str, taxid: int) -> dict:
    records = _fetch_records_for_taxid(taxid)
    summaries = []
    for record in records:
        genes = sorted(
            {
                gene
                for feature in record.features
                for gene in feature.qualifiers.get("gene", [])
                if gene
            },
            key=str.casefold,
        )
        summary = {
            "accession": record.id,
            "length": len(record.seq),
            "description": record.description,
            "genes": genes,
        }
        summary["sequence_class"] = classify_record(
            summary["description"], summary["length"], summary["genes"]
        )
        summaries.append(summary)

    summaries.sort(key=lambda row: (-row["length"], row["accession"]))
    classes: dict[str, int] = {}
    for row in summaries:
        classes[row["sequence_class"]] = classes.get(row["sequence_class"], 0) + 1

    extra = [
        row
        for row in summaries
        if row["sequence_class"] in {
            "COMPLETE_PLASTOME",
            "ADDITIONAL_ANNOTATED_LOCUS",
            "OTHER_LONG_RECORD",
        }
    ]
    return {
        "label": label,
        "taxid": taxid,
        "nucleotide_record_count": len(summaries),
        "sequence_class_counts": dict(sorted(classes.items())),
        "potentially_informative_beyond_ndhF_rbcL": extra,
        "records": summaries,
    }


def run_inventory(output_path: Path) -> dict:
    taxa = {
        "Pontederia cyanea": 44969,
        "Pontederia australasica": 2861341,
        "Pontederia korsakowii": 44971,
        "Pontederia vaginalis": 44972,
    }
    out = {
        "analysis": "balance_u3_monochoria_ncbi_nucleotide_inventory",
        "taxa": {
            label: summarize_taxon(label, taxid)
            for label, taxid in taxa.items()
        },
        "claim_ceiling": (
            "ncbi_public_nucleotide_availability_audit_only_"
            "not_phylogenetic_inference_not_control_adjudication"
        ),
    }
    output_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_inventory(args.output)
    compact = {
        "analysis": result["analysis"],
        "taxa": {
            label: {
                "taxid": taxon["taxid"],
                "nucleotide_record_count": taxon["nucleotide_record_count"],
                "sequence_class_counts": taxon["sequence_class_counts"],
                "potentially_informative_beyond_ndhF_rbcL": taxon[
                    "potentially_informative_beyond_ndhF_rbcL"
                ],
            }
            for label, taxon in result["taxa"].items()
        },
        "claim_ceiling": result["claim_ceiling"],
    }
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
