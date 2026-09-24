"""Rooted plastome-topology audit for unresolved U3 Monochoria controls.

The existing high-resolution audit ranks candidate controls by common-site
plastome p-distance. This module adds the missing topology layer: reference
Monochoria plastomes plus Pontederia cordata as an outgroup are reduced to a
shared single-copy CDS set, aligned gene-by-gene, and analysed with a rooted
neighbor-joining topology plus a gene-block bootstrap.

The result is a plastid topology diagnostic. It is not a nuclear species tree,
not a pollination receipt, and not by itself a matched-control adjudication.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import time
from io import StringIO
from pathlib import Path

from .monochoria_plastome_audit import (
    CORE_SINGLE_COPY_CDS,
    _align,
    _fetch_genbank,
    _write_fasta,
    extract_unambiguous_core_cds,
)


FIELDS = ("taxon", "role", "accession", "source_basis", "notes")
ROLES = {"OUTGROUP", "CANDIDATE", "CASE", "REFERENCE"}
OUTGROUP = "Pontederia cordata"
CASE_TAXA = ("Pontederia korsakowii", "Pontederia vaginalis")
CANDIDATE_TAXA = ("Pontederia australasica", "Pontederia cyanea")


def load_topology_ledger(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("Monochoria topology ledger columns must match canonical order")
        rows = list(reader)
    if len(rows) < 8:
        raise ValueError("Monochoria topology audit requires focal taxa plus reference backbone")

    seen_taxa: set[str] = set()
    seen_accessions: set[str] = set()
    role_counts = {role: 0 for role in ROLES}
    out = []
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside topology ledger schema")
        clean = {k: (v or "").strip() for k, v in row.items()}
        if not clean["taxon"] or clean["taxon"] in seen_taxa:
            raise ValueError(f"row {n} taxon must be unique and frozen")
        if clean["role"] not in ROLES:
            raise ValueError(f"row {n} invalid role")
        if not clean["accession"] or clean["accession"] in seen_accessions:
            raise ValueError(f"row {n} accession must be unique and frozen")
        if not clean["source_basis"]:
            raise ValueError(f"row {n} source_basis must be frozen")
        seen_taxa.add(clean["taxon"])
        seen_accessions.add(clean["accession"])
        role_counts[clean["role"]] += 1
        out.append(clean)

    required = {OUTGROUP, *CASE_TAXA, *CANDIDATE_TAXA}
    if not required.issubset(seen_taxa):
        raise ValueError("topology ledger is missing one or more focal/outgroup taxa")
    if role_counts["OUTGROUP"] != 1:
        raise ValueError("topology ledger requires exactly one outgroup")
    by_taxon = {row["taxon"]: row for row in out}
    if by_taxon[OUTGROUP]["role"] != "OUTGROUP":
        raise ValueError("Pontederia cordata must be the registered outgroup")
    if any(by_taxon[t]["role"] != "CASE" for t in CASE_TAXA):
        raise ValueError("case taxa must retain CASE role")
    if any(by_taxon[t]["role"] != "CANDIDATE" for t in CANDIDATE_TAXA):
        raise ValueError("candidate taxa must retain CANDIDATE role")
    return out


def _pair_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def gene_pair_counts(aligned_by_gene: dict[str, dict[str, str]], taxa: list[str]) -> dict:
    """Precompute mismatch/comparable counts for every gene and taxon pair."""
    valid = set("ACGT")
    result: dict[str, dict[tuple[str, str], tuple[int, int]]] = {}
    for gene, aligned in sorted(aligned_by_gene.items()):
        if set(aligned) != set(taxa):
            raise ValueError(f"{gene} alignment taxon set disagrees with topology ledger")
        counts = {}
        for i, a in enumerate(taxa):
            for b in taxa[:i]:
                comparable = 0
                differences = 0
                for x, y in zip(aligned[a].upper(), aligned[b].upper()):
                    if x not in valid or y not in valid:
                        continue
                    comparable += 1
                    differences += x != y
                if comparable == 0:
                    raise ValueError(f"{gene} has no comparable sites for {a} versus {b}")
                counts[_pair_key(a, b)] = (differences, comparable)
        result[gene] = counts
    return result


def distance_matrix_from_counts(
    taxa: list[str],
    per_gene_counts: dict[str, dict[tuple[str, str], tuple[int, int]]],
    sampled_genes: list[str] | None = None,
):
    genes = sampled_genes if sampled_genes is not None else list(per_gene_counts)
    if not genes:
        raise ValueError("at least one gene is required for a topology distance matrix")
    matrix = []
    for i, a in enumerate(taxa):
        row = []
        for j, b in enumerate(taxa[: i + 1]):
            if i == j:
                row.append(0.0)
                continue
            diff = 0
            comp = 0
            key = _pair_key(a, b)
            for gene in genes:
                d, c = per_gene_counts[gene][key]
                diff += d
                comp += c
            if comp == 0:
                raise ValueError(f"no comparable sites for {a} versus {b}")
            row.append(diff / comp)
        matrix.append(row)
    from Bio.Phylo.TreeConstruction import DistanceMatrix
    return DistanceMatrix(taxa, matrix)


def build_rooted_nj_tree(distance_matrix, outgroup: str = OUTGROUP):
    from Bio.Phylo.TreeConstruction import DistanceTreeConstructor
    tree = DistanceTreeConstructor().nj(distance_matrix)
    matches = [terminal for terminal in tree.get_terminals() if terminal.name == outgroup]
    if len(matches) != 1:
        raise ValueError("registered outgroup must occur exactly once in NJ tree")
    tree.root_with_outgroup(matches[0])
    return tree


def compare_candidate_topology(tree, case_taxon: str) -> dict:
    terminals = {terminal.name for terminal in tree.get_terminals()}
    needed = {case_taxon, *CANDIDATE_TAXA}
    if not needed.issubset(terminals):
        raise ValueError("tree is missing focal case/candidate taxa")

    depths = tree.depths(unit_branch_lengths=True)
    mrca_depths = {}
    patristic = {}
    for candidate in CANDIDATE_TAXA:
        mrca = tree.common_ancestor(case_taxon, candidate)
        mrca_depths[candidate] = int(depths[mrca])
        patristic[candidate] = float(tree.distance(case_taxon, candidate))

    a, b = CANDIDATE_TAXA
    if mrca_depths[a] > mrca_depths[b]:
        winner = a
        outcome = "MORE_RECENT_MRCA"
    elif mrca_depths[b] > mrca_depths[a]:
        winner = b
        outcome = "MORE_RECENT_MRCA"
    else:
        winner = None
        outcome = "EQUAL_MRCA_DEPTH"

    return {
        "case_taxon": case_taxon,
        "mrca_edge_depths": mrca_depths,
        "topology_outcome": outcome,
        "topology_winner": winner,
        "patristic_distances_diagnostic_only": patristic,
    }


def bootstrap_topology(
    taxa: list[str],
    per_gene_counts: dict[str, dict[tuple[str, str], tuple[int, int]]],
    n_replicates: int = 500,
    seed: int = 20260924,
) -> dict:
    if n_replicates < 1:
        raise ValueError("bootstrap replicate count must be positive")
    genes = list(per_gene_counts)
    rng = random.Random(seed)
    counts = {
        case: {CANDIDATE_TAXA[0]: 0, CANDIDATE_TAXA[1]: 0, "TIE": 0}
        for case in CASE_TAXA
    }
    for _ in range(n_replicates):
        sampled = [rng.choice(genes) for _ in genes]
        dm = distance_matrix_from_counts(taxa, per_gene_counts, sampled)
        tree = build_rooted_nj_tree(dm)
        for case in CASE_TAXA:
            cmp = compare_candidate_topology(tree, case)
            winner = cmp["topology_winner"] or "TIE"
            counts[case][winner] += 1
    return {
        "replicates": n_replicates,
        "seed": seed,
        "counts": counts,
        "fractions": {
            case: {key: value / n_replicates for key, value in row.items()}
            for case, row in counts.items()
        },
    }


def _newick(tree) -> str:
    from Bio import Phylo
    handle = StringIO()
    Phylo.write(tree, handle, "newick")
    return handle.getvalue().strip()


def run_topology_audit(
    ledger_path: Path,
    output_path: Path,
    workdir: Path,
    bootstrap_replicates: int = 500,
) -> dict:
    rows = load_topology_ledger(ledger_path)
    workdir.mkdir(parents=True, exist_ok=True)
    taxa = [row["taxon"] for row in rows]

    extracted: dict[str, dict[str, str]] = {}
    record_lengths = {}
    for row in rows:
        record = _fetch_genbank(row["accession"])
        record_lengths[row["taxon"]] = len(record.seq)
        genes, _ = extract_unambiguous_core_cds(record)
        extracted[row["taxon"]] = genes
        time.sleep(0.35)

    shared_genes = [
        gene for gene in CORE_SINGLE_COPY_CDS
        if all(gene in extracted[taxon] for taxon in taxa)
    ]
    if len(shared_genes) < 30:
        raise ValueError(f"too few shared CDS for topology audit: {len(shared_genes)}")

    aligned_by_gene = {}
    for gene in shared_genes:
        aligned_by_gene[gene] = _align(
            {taxon: extracted[taxon][gene] for taxon in taxa}, gene, workdir
        )

    concatenated = {
        taxon: "".join(aligned_by_gene[gene][taxon] for gene in shared_genes)
        for taxon in taxa
    }
    _write_fasta(concatenated, workdir / "topology_shared_core_cds.aligned.fasta")

    counts = gene_pair_counts(aligned_by_gene, taxa)
    dm = distance_matrix_from_counts(taxa, counts)
    tree = build_rooted_nj_tree(dm)
    comparisons = {case: compare_candidate_topology(tree, case) for case in CASE_TAXA}
    bootstrap = bootstrap_topology(taxa, counts, bootstrap_replicates)

    out = {
        "analysis": "balance_u3_monochoria_rooted_plastome_topology_audit",
        "method": (
            "shared single-copy plastome CDS; per-gene MAFFT; nucleotide-count "
            "p-distance matrix; neighbor joining rooted on Pontederia cordata; "
            "gene-block bootstrap"
        ),
        "accessions": {row["taxon"]: row["accession"] for row in rows},
        "record_lengths": record_lengths,
        "shared_gene_count": len(shared_genes),
        "shared_genes": shared_genes,
        "concatenated_alignment_length": len(next(iter(concatenated.values()))),
        "rooted_newick": _newick(tree),
        "case_comparisons": comparisons,
        "gene_block_bootstrap": bootstrap,
        "adjudication_rule": (
            "topology_precedes_branch_length_or_common_site_distance; if candidates "
            "have equal MRCA depth, the preregistered better-resolved phylogenetic-"
            "distance tie-break may be consulted separately"
        ),
        "claim_ceiling": (
            "rooted_plastome_topology_candidate_ranking_diagnostic_only_"
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
    parser.add_argument("--bootstrap-replicates", type=int, default=500)
    args = parser.parse_args()
    result = run_topology_audit(
        args.ledger, args.output, args.workdir, args.bootstrap_replicates
    )
    compact = {
        "analysis": result["analysis"],
        "shared_gene_count": result["shared_gene_count"],
        "rooted_newick": result["rooted_newick"],
        "case_comparisons": result["case_comparisons"],
        "gene_block_bootstrap": result["gene_block_bootstrap"],
        "adjudication_rule": result["adjudication_rule"],
        "claim_ceiling": result["claim_ceiling"],
    }
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
