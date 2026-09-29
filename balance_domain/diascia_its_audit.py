"""Public-ITS proximity audit for the active U3 Diascia control search.

The audit inventories public NCBI nucleotide records for Diascia, selects at
most one ITS-like record per exact species using a deterministic,
outcome-blind sequence-completeness rule, aligns the selected sequences with
MAFFT, and reports:

1. pairwise p-distance from the case Diascia anastrepta to every represented
   species;
2. one joint-site comparison among the registered nonheterantherous control
   candidates with direct pollination evidence;
3. the positions of the two close heterantherous exclusions D. megathura and
   D. purpurea.

This is a molecular-proximity diagnostic, not a definitive species tree and
not a control adjudication by itself.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from collections import defaultdict
from pathlib import Path

from .monochoria_common_marker import compare_candidates_on_common_sites, p_distance

DIASCIA_TAXID = 255860
CASE_TAXON = "Diascia anastrepta"
CLOSE_HETERANTHERY_EXCLUSIONS = (
    "Diascia megathura",
    "Diascia purpurea",
)
REGISTERED_CONTROL_CANDIDATES = (
    "Diascia barberae",
    "Diascia cordata",
    "Diascia integerrima",
)
HIGH_VALUE_TAXA = (
    CASE_TAXON,
    *CLOSE_HETERANTHERY_EXCLUSIONS,
    *REGISTERED_CONTROL_CANDIDATES,
    "Diascia vigilis",
    "Diascia lilacina",
)

ITS_TOKEN_RE = re.compile(
    r"(internal transcribed spacer|\bits ?1\b|\bits ?2\b|\bits\b)",
    re.IGNORECASE,
)
UNRESOLVED_TAXON_MARKERS = (" sp.", " cf.", " aff.", " x ", " hybrid")


def is_exact_species_name(name: str) -> bool:
    clean = " ".join(name.split())
    if not clean.startswith("Diascia "):
        return False
    lowered = clean.casefold()
    if any(marker in lowered for marker in UNRESOLVED_TAXON_MARKERS):
        return False
    parts = clean.split()
    return len(parts) == 2 and parts[1][0].islower()


def its_record_score(description: str, sequence: str, accession: str) -> tuple:
    """Outcome-blind deterministic ranking for one species' ITS records.

    Higher values are better except accession, which is reversed by sorting
    separately. Preference order:
    - title explicitly names both ITS1 and ITS2;
    - title names an internal transcribed spacer / ITS;
    - sequence lies in the broad full-ITS length window;
    - fewer ambiguous bases;
    - longer sequence up to 1200 bp.
    """
    desc = description.casefold()
    has_its1 = "internal transcribed spacer 1" in desc or re.search(r"\bits ?1\b", desc)
    has_its2 = "internal transcribed spacer 2" in desc or re.search(r"\bits ?2\b", desc)
    full_both = bool(has_its1 and has_its2)
    any_its = bool(ITS_TOKEN_RE.search(description))
    length = len(sequence)
    full_window = 450 <= length <= 1000
    ambiguous = sum(base not in "ACGT" for base in sequence.upper())
    capped_length = min(length, 1200)
    return (
        int(full_both),
        int(any_its),
        int(full_window),
        -ambiguous,
        capped_length,
        accession,
    )


def select_representatives(records: list[dict]) -> dict[str, dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in records:
        taxon = " ".join(row["taxon"].split())
        if not is_exact_species_name(taxon):
            continue
        if not ITS_TOKEN_RE.search(row["description"]):
            continue
        grouped[taxon].append(row)

    selected: dict[str, dict] = {}
    for taxon, options in sorted(grouped.items()):
        # accession is a final deterministic lexical tie-break but should sort
        # ascending; all biological/completeness components sort descending.
        ranked = sorted(
            options,
            key=lambda row: (
                tuple(-x if isinstance(x, int) else x for x in its_record_score(
                    row["description"], row["sequence"], row["accession"]
                )[:-1]),
                row["accession"],
            ),
        )
        selected[taxon] = ranked[0]
    return selected


def _fetch_genus_records() -> list[dict]:
    from Bio import Entrez, SeqIO

    Entrez.email = "balance-diascia-its-audit@users.noreply.github.com"
    with Entrez.esearch(
        db="nuccore",
        term=f"txid{DIASCIA_TAXID}[Organism:exp]",
        retmax=1000,
    ) as handle:
        search = Entrez.read(handle)
    ids = list(search.get("IdList", []))
    count = int(search.get("Count", 0))
    if count != len(ids):
        raise ValueError(
            f"Diascia NCBI search returned {count} records but only "
            f"{len(ids)} IDs; raise retmax"
        )

    rows: list[dict] = []
    for start in range(0, len(ids), 50):
        chunk = ids[start : start + 50]
        with Entrez.efetch(
            db="nuccore",
            id=",".join(chunk),
            rettype="gbwithparts",
            retmode="text",
        ) as handle:
            for record in SeqIO.parse(handle, "genbank"):
                taxon = str(record.annotations.get("organism", "")).strip()
                sequence = str(record.seq).upper()
                rows.append(
                    {
                        "taxon": taxon,
                        "accession": record.id,
                        "description": record.description,
                        "length": len(sequence),
                        "sequence": sequence,
                    }
                )
        time.sleep(0.35)
    return rows


def _write_fasta(records: dict[str, str], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for taxon, seq in records.items():
            handle.write(f">{taxon.replace(' ', '_')}\n")
            for i in range(0, len(seq), 80):
                handle.write(seq[i:i+80] + "\n")


def _read_fasta(path: Path) -> dict[str, str]:
    from Bio import SeqIO

    return {
        rec.id.replace("_", " "): str(rec.seq).upper()
        for rec in SeqIO.parse(path, "fasta")
    }


def _align(records: dict[str, str], workdir: Path) -> dict[str, str]:
    raw = workdir / "diascia_its.raw.fasta"
    aligned = workdir / "diascia_its.aligned.fasta"
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
        raise RuntimeError(f"MAFFT failed: {proc.stderr.strip()}")
    result = _read_fasta(aligned)
    if set(result) != set(records):
        raise ValueError("Diascia ITS alignment changed the selected taxon set")
    return result


def _pairwise_case_distances(aligned: dict[str, str]) -> dict[str, dict]:
    if CASE_TAXON not in aligned:
        raise ValueError(f"public ITS inventory lacks required case {CASE_TAXON}")
    return {
        taxon: p_distance(aligned[CASE_TAXON], seq)
        for taxon, seq in sorted(aligned.items())
        if taxon != CASE_TAXON
    }


def _nj_tree(aligned: dict[str, str], output_path: Path) -> dict:
    """Build a descriptive NJ tree from pairwise masked p-distances."""
    from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor
    from Bio import Phylo

    taxa = sorted(aligned)
    matrix: list[list[float]] = []
    for i, a in enumerate(taxa):
        row = []
        for b in taxa[: i + 1]:
            if a == b:
                row.append(0.0)
            else:
                row.append(float(p_distance(aligned[a], aligned[b])["p_distance"]))
        matrix.append(row)
    dm = DistanceMatrix(names=taxa, matrix=matrix)
    tree = DistanceTreeConstructor().nj(dm)
    Phylo.write(tree, output_path, "newick")

    case = next(tree.find_clades(name=CASE_TAXON))
    patristic = {}
    for taxon in taxa:
        if taxon == CASE_TAXON:
            continue
        target = next(tree.find_clades(name=taxon))
        patristic[taxon] = tree.distance(case, target)
    ordered = sorted(patristic, key=lambda t: (patristic[t], t))
    return {
        "newick_path": str(output_path),
        "case_patristic_distances": {
            taxon: patristic[taxon] for taxon in ordered
        },
        "nearest_case_taxa_by_nj_patristic_distance": ordered[:10],
    }


def run_audit(output_path: Path, workdir: Path) -> dict:
    workdir.mkdir(parents=True, exist_ok=True)
    raw_records = _fetch_genus_records()
    selected = select_representatives(raw_records)

    missing_high_value = [taxon for taxon in HIGH_VALUE_TAXA if taxon not in selected]

    raw_counts = defaultdict(int)
    for row in raw_records:
        taxon = " ".join(row["taxon"].split())
        if taxon:
            raw_counts[taxon] += 1

    sequences = {
        taxon: row["sequence"]
        for taxon, row in selected.items()
    }
    if CASE_TAXON not in sequences:
        output = {
            "analysis": "balance_u3_diascia_public_its_proximity_audit_v1",
            "status": "CASE_ITS_UNAVAILABLE",
            "ncbi_genus_taxid": DIASCIA_TAXID,
            "n_nucleotide_records_in_genus_inventory": len(raw_records),
            "n_exact_species_with_selected_its": len(selected),
            "high_value_raw_record_counts": {
                taxon: raw_counts.get(taxon, 0) for taxon in HIGH_VALUE_TAXA
            },
            "selection_rule": (
                "one_exact_species_record_selected_without_distance_outcomes_by_"
                "ITS1_ITS2_title_completeness_then_full_length_window_then_"
                "ambiguity_then_length_then_accession"
            ),
            "selected_records": {
                taxon: {
                    "accession": row["accession"],
                    "description": row["description"],
                    "length": row["length"],
                }
                for taxon, row in sorted(selected.items())
            },
            "missing_high_value_taxa": missing_high_value,
            "case_taxon": CASE_TAXON,
            "next_gate": (
                "public_NCBI_ITS_cannot_rank_controls_without_case_sequence; "
                "use source-published topology or a higher-resolution public surface"
            ),
            "claim_ceiling": (
                "public_NCBI_ITS_availability_ceiling_only_not_phylogenetic_ranking_"
                "not_control_adjudication"
            ),
        }
        output_path.write_text(
            json.dumps(output, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return output
    aligned = _align(sequences, workdir)

    pairwise = _pairwise_case_distances(aligned)
    ordered_pairwise = sorted(
        pairwise,
        key=lambda taxon: (
            pairwise[taxon]["p_distance"],
            -pairwise[taxon]["comparable_sites"],
            taxon,
        ),
    )

    joint_candidate_result = None
    present_registered = [
        taxon for taxon in REGISTERED_CONTROL_CANDIDATES if taxon in aligned
    ]
    if len(present_registered) >= 2:
        joint_candidate_result = compare_candidates_on_common_sites(
            aligned,
            CASE_TAXON,
            candidate_taxa=present_registered,
        )

    exclusion_distances = {
        taxon: pairwise[taxon]
        for taxon in CLOSE_HETERANTHERY_EXCLUSIONS
        if taxon in pairwise
    }
    candidate_distances = {
        taxon: pairwise[taxon]
        for taxon in REGISTERED_CONTROL_CANDIDATES
        if taxon in pairwise
    }

    tree_readout = _nj_tree(aligned, workdir / "diascia_its.nwk")

    output = {
        "analysis": "balance_u3_diascia_public_its_proximity_audit_v1",
        "status": "PROXIMITY_DIAGNOSTIC_AVAILABLE",
        "ncbi_genus_taxid": DIASCIA_TAXID,
        "n_nucleotide_records_in_genus_inventory": len(raw_records),
        "n_exact_species_with_selected_its": len(selected),
        "selection_rule": (
            "one_exact_species_record_selected_without_distance_outcomes_by_"
            "ITS1_ITS2_title_completeness_then_full_length_window_then_"
            "ambiguity_then_length_then_accession"
        ),
        "selected_records": {
            taxon: {
                "accession": row["accession"],
                "description": row["description"],
                "length": row["length"],
            }
            for taxon, row in sorted(selected.items())
        },
        "missing_high_value_taxa": missing_high_value,
        "case_taxon": CASE_TAXON,
        "case_pairwise_p_distances": {
            taxon: pairwise[taxon] for taxon in ordered_pairwise
        },
        "nearest_case_taxa_by_pairwise_p_distance": ordered_pairwise[:15],
        "close_heteranthery_exclusion_distances": exclusion_distances,
        "registered_control_candidate_distances": candidate_distances,
        "registered_control_candidates_joint_site_comparison": joint_candidate_result,
        "nj_tree": tree_readout,
        "claim_ceiling": (
            "public_ITS_proximity_and_descriptive_NJ_diagnostic_only_"
            "not_definitive_species_tree_not_heteranthery_absence_"
            "not_pollination_receipt_not_control_adjudication"
        ),
    }
    output_path.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    args = parser.parse_args()
    result = run_audit(args.output, args.workdir)
    compact = {
        key: result[key]
        for key in (
            "analysis",
            "status",
            "n_nucleotide_records_in_genus_inventory",
            "n_exact_species_with_selected_its",
            "high_value_raw_record_counts",
            "missing_high_value_taxa",
            "selected_records",
            "nearest_case_taxa_by_pairwise_p_distance",
            "close_heteranthery_exclusion_distances",
            "registered_control_candidate_distances",
            "registered_control_candidates_joint_site_comparison",
            "nj_tree",
            "next_gate",
            "claim_ceiling",
        )
        if key in result
    }
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
