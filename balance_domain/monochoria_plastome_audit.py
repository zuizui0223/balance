"""High-resolution plastome-CDS audit for unresolved U3 Monochoria controls.

Four complete plastomes are reduced to a preregistered set of single-copy
chloroplast protein-coding genes. Each gene is aligned separately with MAFFT,
then concatenated. Candidate ranking uses one joint A/C/G/T site mask across
the case and both candidate controls. Gene-wise support is reported alongside
the concatenated distance so the result does not rest on one locus.

This remains a plastid-proximity diagnostic, not a nuclear species tree.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import time
from pathlib import Path

from .monochoria_common_marker import compare_candidates_on_common_sites


FIELDS = ("taxon", "role", "accession", "selection_basis", "notes")
ROLES = {"CANDIDATE", "CASE"}

CASE_TAXA = ("Pontederia korsakowii", "Pontederia vaginalis")
CANDIDATE_TAXA = ("Pontederia australasica", "Pontederia cyanea")

# Excludes IR-duplicated and awkward trans-spliced genes (e.g. rps12), genes
# commonly present as pseudogenes, and ycf1/ycf2 boundary-copy complications.
CORE_SINGLE_COPY_CDS = (
    "accD",
    "atpA", "atpB", "atpE", "atpF", "atpH", "atpI",
    "ccsA", "cemA", "matK",
    "ndhA", "ndhC", "ndhD", "ndhE", "ndhF", "ndhG", "ndhH", "ndhI", "ndhJ", "ndhK",
    "petA", "petB", "petD", "petG", "petL", "petN",
    "psaA", "psaB", "psaC", "psaI", "psaJ",
    "psbA", "psbB", "psbC", "psbD", "psbE", "psbF", "psbH", "psbI",
    "psbJ", "psbK", "psbL", "psbM", "psbN", "psbT", "psbZ",
    "rbcL",
    "rpl14", "rpl16", "rpl20", "rpl22", "rpl32", "rpl33", "rpl36",
    "rpoA", "rpoB", "rpoC1", "rpoC2",
    "rps2", "rps3", "rps4", "rps8", "rps11", "rps14", "rps15", "rps16", "rps18",
    "ycf3", "ycf4",
)


def load_plastome_ledger(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("Monochoria plastome ledger columns must match canonical order")
        rows = list(reader)
    if len(rows) != 4:
        raise ValueError("Monochoria plastome audit requires exactly four focal taxa")

    seen_taxa: set[str] = set()
    seen_accessions: set[str] = set()
    for n, row in enumerate(rows, start=2):
        clean = {k: (v or "").strip() for k, v in row.items()}
        if not clean["taxon"] or clean["taxon"] in seen_taxa:
            raise ValueError(f"row {n} taxon must be unique and frozen")
        if clean["role"] not in ROLES:
            raise ValueError(f"row {n} invalid role")
        if not clean["accession"] or clean["accession"] in seen_accessions:
            raise ValueError(f"row {n} accession must be unique and frozen")
        if not clean["selection_basis"]:
            raise ValueError(f"row {n} selection_basis must be frozen")
        seen_taxa.add(clean["taxon"])
        seen_accessions.add(clean["accession"])
        row.update(clean)

    required = set(CASE_TAXA) | set(CANDIDATE_TAXA)
    if seen_taxa != required:
        raise ValueError("plastome ledger must contain exactly the two cases and two candidates")
    return rows


def _fetch_genbank(accession: str):
    from Bio import Entrez, SeqIO

    Entrez.email = "balance-plastome-audit@users.noreply.github.com"
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with Entrez.efetch(
                db="nuccore",
                id=accession,
                rettype="gbwithparts",
                retmode="text",
            ) as handle:
                return SeqIO.read(handle, "genbank")
        except Exception as exc:  # pragma: no cover - network path
            last_error = exc
            time.sleep(1.0 + attempt)
    raise RuntimeError(f"failed to fetch {accession}") from last_error


def extract_unambiguous_core_cds(record) -> tuple[dict[str, str], dict[str, str]]:
    """Return unambiguous core CDS and reasons for skipped registered genes."""
    by_gene: dict[str, list[str]] = {}
    for feature in record.features:
        if feature.type != "CDS":
            continue
        if "pseudo" in feature.qualifiers or "pseudogene" in feature.qualifiers:
            continue
        genes = feature.qualifiers.get("gene", [])
        if len(genes) != 1:
            continue
        gene = genes[0]
        if gene not in CORE_SINGLE_COPY_CDS:
            continue
        seq = str(feature.extract(record.seq)).upper()
        if len(seq) < 90:
            continue
        by_gene.setdefault(gene, []).append(seq)

    out: dict[str, str] = {}
    skipped: dict[str, str] = {}
    for gene in CORE_SINGLE_COPY_CDS:
        seqs = by_gene.get(gene, [])
        unique = sorted(set(seqs))
        if not unique:
            skipped[gene] = "MISSING_OR_UNANNOTATED"
        elif len(unique) > 1:
            skipped[gene] = "MULTIPLE_NONIDENTICAL_CDS_COPIES"
        else:
            out[gene] = unique[0]
    return out, skipped


def _write_fasta(records: dict[str, str], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for name, seq in records.items():
            handle.write(f">{name.replace(' ', '_')}\n")
            for i in range(0, len(seq), 80):
                handle.write(seq[i : i + 80] + "\n")


def _read_fasta(path: Path) -> dict[str, str]:
    from Bio import SeqIO
    return {
        rec.id.replace("_", " "): str(rec.seq).upper()
        for rec in SeqIO.parse(path, "fasta")
    }


def _align(records: dict[str, str], gene: str, workdir: Path) -> dict[str, str]:
    raw = workdir / f"{gene}.raw.fasta"
    aligned = workdir / f"{gene}.aligned.fasta"
    _write_fasta(records, raw)
    with aligned.open("w", encoding="utf-8") as out:
        proc = subprocess.run(
            ["mafft", "--auto", "--quiet", str(raw)],
            stdout=out,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    if proc.returncode != 0:
        raise RuntimeError(f"MAFFT failed for {gene}: {proc.stderr.strip()}")
    result = _read_fasta(aligned)
    if set(result) != set(records):
        raise ValueError(f"{gene} alignment changed the registered taxon set")
    return result


def summarize_gene_support(
    aligned_by_gene: dict[str, dict[str, str]],
    case_taxon: str,
) -> dict:
    counts = {
        "Pontederia australasica": 0,
        "Pontederia cyanea": 0,
        "TIE": 0,
    }
    per_gene = {}
    for gene, aligned in sorted(aligned_by_gene.items()):
        comparison = compare_candidates_on_common_sites(aligned, case_taxon)
        winner = comparison["closest_candidate_by_p_distance"]
        counts[winner if winner is not None else "TIE"] += 1
        per_gene[gene] = {
            "jointly_comparable_sites": comparison["jointly_comparable_sites"],
            "candidate_distances": comparison["candidate_distances"],
            "outcome": comparison["distance_outcome"],
            "winner": winner,
        }
    return {"support_counts": counts, "per_gene": per_gene}


def run_plastome_audit(ledger_path: Path, output_path: Path, workdir: Path) -> dict:
    rows = load_plastome_ledger(ledger_path)
    workdir.mkdir(parents=True, exist_ok=True)

    extracted: dict[str, dict[str, str]] = {}
    skipped: dict[str, dict[str, str]] = {}
    record_lengths = {}
    for row in rows:
        record = _fetch_genbank(row["accession"])
        record_lengths[row["taxon"]] = len(record.seq)
        genes, skipped_genes = extract_unambiguous_core_cds(record)
        extracted[row["taxon"]] = genes
        skipped[row["taxon"]] = skipped_genes
        time.sleep(0.4)

    shared_genes = [
        gene
        for gene in CORE_SINGLE_COPY_CDS
        if all(gene in extracted[taxon] for taxon in extracted)
    ]
    if len(shared_genes) < 30:
        raise ValueError(
            f"too few shared single-copy CDS for high-resolution audit: {len(shared_genes)}"
        )

    aligned_by_gene = {}
    for gene in shared_genes:
        aligned_by_gene[gene] = _align(
            {taxon: extracted[taxon][gene] for taxon in extracted},
            gene,
            workdir,
        )

    concatenated = {
        taxon: "".join(aligned_by_gene[gene][taxon] for gene in shared_genes)
        for taxon in extracted
    }
    _write_fasta(concatenated, workdir / "shared_core_cds.aligned.fasta")

    comparisons = {
        case: compare_candidates_on_common_sites(concatenated, case)
        for case in CASE_TAXA
    }
    gene_support = {
        case: summarize_gene_support(aligned_by_gene, case)
        for case in CASE_TAXA
    }

    candidate_pair = compare_candidates_on_common_sites(
        {
            "Pontederia australasica": concatenated["Pontederia australasica"],
            "Pontederia cyanea": concatenated["Pontederia cyanea"],
            # Dummy case equal to australasica lets the helper expose the
            # candidate-candidate joint-site differences without a new mask.
            "Pontederia korsakowii": concatenated["Pontederia australasica"],
        },
        "Pontederia korsakowii",
    )

    out = {
        "analysis": "balance_u3_monochoria_shared_plastome_cds_audit",
        "accessions": {row["taxon"]: row["accession"] for row in rows},
        "record_lengths": record_lengths,
        "registered_core_gene_count": len(CORE_SINGLE_COPY_CDS),
        "shared_gene_count": len(shared_genes),
        "shared_genes": shared_genes,
        "skipped_registered_genes": skipped,
        "concatenated_alignment_length": len(next(iter(concatenated.values()))),
        "candidate_pair_differences_on_shared_cds": candidate_pair[
            "candidate_pair_differences_on_joint_sites"
        ],
        "case_comparisons": comparisons,
        "gene_wise_support": gene_support,
        "claim_ceiling": (
            "shared_single_copy_plastome_CDS_proximity_diagnostic_only_"
            "not_nuclear_species_tree_not_pollination_receipt_not_historical_causation"
        ),
    }
    output_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    args = parser.parse_args()
    result = run_plastome_audit(args.ledger, args.output, args.workdir)
    compact = {
        "analysis": result["analysis"],
        "accessions": result["accessions"],
        "record_lengths": result["record_lengths"],
        "shared_gene_count": result["shared_gene_count"],
        "shared_genes": result["shared_genes"],
        "concatenated_alignment_length": result["concatenated_alignment_length"],
        "candidate_pair_differences_on_shared_cds": result[
            "candidate_pair_differences_on_shared_cds"
        ],
        "case_comparisons": result["case_comparisons"],
        "gene_wise_support": {
            case: support["support_counts"]
            for case, support in result["gene_wise_support"].items()
        },
        "claim_ceiling": result["claim_ceiling"],
    }
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
