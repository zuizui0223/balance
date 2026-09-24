"""Reproducible common-marker audit for the two open U3 Monochoria controls.

The audit places P. australasica and P. cyanea on the same chloroplast
coordinates as the two U3 case taxa using ndhF + rbcL. Network access and
MAFFT are required only by the CLI execution path; schema and distance helpers
remain testable without external dependencies.

Candidate ranking is deliberately restricted to sites that are comparable in
the case and *all* candidate controls. Pairwise p-distances over different site
sets are retained as diagnostics only and are never used to choose a control.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import time
from pathlib import Path
from typing import Iterable


FIELDS = (
    "taxon",
    "role",
    "record_type",
    "ndhf_accession",
    "rbcl_accession",
    "source_basis",
    "notes",
)
ROLES = {"CANDIDATE", "CASE", "REFERENCE", "OUTGROUP"}
RECORD_TYPES = {"COMPLETE_PLASTOME", "GENE_ACCESSIONS"}
GENES = ("ndhF", "rbcL")

CASE_TAXA = ("Pontederia korsakowii", "Pontederia vaginalis")
CANDIDATE_TAXA = ("Pontederia australasica", "Pontederia cyanea")


def load_accession_ledger(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("Monochoria common-marker ledger columns must match canonical order")
        rows = list(reader)

    if not rows:
        raise ValueError("Monochoria common-marker ledger must not be empty")

    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside common-marker schema")
        clean = {k: (v or "").strip() for k, v in row.items()}
        if not clean["taxon"] or clean["taxon"] in seen:
            raise ValueError(f"row {n} taxon must be unique and frozen")
        seen.add(clean["taxon"])
        if clean["role"] not in ROLES:
            raise ValueError(f"row {n} invalid role")
        if clean["record_type"] not in RECORD_TYPES:
            raise ValueError(f"row {n} invalid record_type")
        if not clean["ndhf_accession"] or not clean["rbcl_accession"]:
            raise ValueError(f"row {n} both marker accessions must be frozen")
        if clean["record_type"] == "COMPLETE_PLASTOME":
            if clean["ndhf_accession"] != clean["rbcl_accession"]:
                raise ValueError(
                    f"row {n} complete-plastome markers must point to one genome accession"
                )
        if not clean["source_basis"]:
            raise ValueError(f"row {n} source_basis must be frozen")
        out.append(clean)

    required = set(CASE_TAXA) | set(CANDIDATE_TAXA)
    missing = required - seen
    if missing:
        raise ValueError("common-marker ledger missing focal taxa: " + ", ".join(sorted(missing)))
    return out


def p_distance(aligned_a: str, aligned_b: str) -> dict[str, float | int]:
    """Gap/ambiguity-masked p-distance on two strings from one MSA."""
    if len(aligned_a) != len(aligned_b):
        raise ValueError("aligned sequences must have equal length")
    valid = set("ACGT")
    comparable = 0
    differences = 0
    for a, b in zip(aligned_a.upper(), aligned_b.upper()):
        if a not in valid or b not in valid:
            continue
        comparable += 1
        differences += a != b
    if comparable == 0:
        raise ValueError("aligned sequences have no comparable A/C/G/T sites")
    return {
        "comparable_sites": comparable,
        "differences": differences,
        "p_distance": differences / comparable,
    }


def compare_candidates_on_common_sites(
    aligned_sequences: dict[str, str],
    case_taxon: str,
    candidate_taxa: Iterable[str] = CANDIDATE_TAXA,
) -> dict:
    """Compare candidates only on the exact same sites for every focal taxon.

    This prevents a long complete-plastome-derived gene from gaining an
    artificial advantage over a historical partial-gene accession merely
    because its pairwise comparison uses more sites.
    """
    candidates = tuple(candidate_taxa)
    if len(candidates) < 2:
        raise ValueError("at least two candidate controls are required")
    focal = (case_taxon, *candidates)
    missing = [taxon for taxon in focal if taxon not in aligned_sequences]
    if missing:
        raise ValueError("missing aligned focal taxa: " + ", ".join(missing))

    lengths = {len(aligned_sequences[taxon]) for taxon in focal}
    if len(lengths) != 1:
        raise ValueError("all focal sequences must come from one equal-length alignment")

    valid = set("ACGT")
    comparable = 0
    differences = {candidate: 0 for candidate in candidates}
    candidate_pair_differences = 0

    seqs = {taxon: aligned_sequences[taxon].upper() for taxon in focal}
    for chars in zip(*(seqs[taxon] for taxon in focal)):
        if any(char not in valid for char in chars):
            continue
        comparable += 1
        case_base = chars[0]
        for idx, candidate in enumerate(candidates, start=1):
            differences[candidate] += chars[idx] != case_base
        if len(candidates) == 2:
            candidate_pair_differences += chars[1] != chars[2]

    if comparable == 0:
        raise ValueError("case and candidates have no jointly comparable A/C/G/T sites")

    distances = {
        candidate: {
            "comparable_sites": comparable,
            "differences": differences[candidate],
            "p_distance": differences[candidate] / comparable,
        }
        for candidate in candidates
    }
    ordered = sorted(candidates, key=lambda taxon: (differences[taxon], taxon))
    best, second = ordered[0], ordered[1]
    if differences[best] == differences[second]:
        outcome = "TIE"
        winner = None
    else:
        outcome = "LOWER_COMMON_SITE_P_DISTANCE"
        winner = best

    return {
        "case_taxon": case_taxon,
        "jointly_comparable_sites": comparable,
        "candidate_distances": distances,
        "candidate_pair_differences_on_joint_sites": (
            candidate_pair_differences if len(candidates) == 2 else None
        ),
        "distance_outcome": outcome,
        "closest_candidate_by_p_distance": winner,
        "difference_count_delta": differences[second] - differences[best],
        "p_distance_delta": (
            differences[second] - differences[best]
        ) / comparable,
        "claim_ceiling": (
            "joint_site_two_plastid_marker_proximity_diagnostic_only_"
            "not_species_tree_not_pollination_receipt_not_control_adjudication"
        ),
    }


def _pair_key(a: str, b: str) -> str:
    return " || ".join(sorted((a, b)))


def _fetch_record(accession: str, rettype: str):
    from Bio import Entrez

    Entrez.email = "balance-common-marker@users.noreply.github.com"
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            handle = Entrez.efetch(
                db="nuccore",
                id=accession,
                rettype=rettype,
                retmode="text",
            )
            return handle
        except Exception as exc:  # pragma: no cover - external network
            last_error = exc
            time.sleep(1.0 + attempt)
    raise RuntimeError(f"failed to fetch {accession} after retries") from last_error


def _fetch_gene(row: dict[str, str], gene: str) -> str:
    from Bio import SeqIO

    accession = row["ndhf_accession"] if gene == "ndhF" else row["rbcl_accession"]
    if row["record_type"] == "GENE_ACCESSIONS":
        with _fetch_record(accession, "fasta") as handle:
            record = SeqIO.read(handle, "fasta")
        seq = str(record.seq).upper()
        if len(seq) < 300:
            raise ValueError(f"{row['taxon']} {gene} sequence unexpectedly short")
        return seq

    with _fetch_record(accession, "gbwithparts") as handle:
        record = SeqIO.read(handle, "genbank")
    matches = []
    for feature in record.features:
        if feature.type not in {"CDS", "gene"}:
            continue
        names = [x.casefold() for x in feature.qualifiers.get("gene", [])]
        if gene.casefold() in names:
            matches.append(feature)
    if not matches:
        raise ValueError(f"{row['taxon']} {accession} has no annotated {gene} feature")
    matches.sort(key=lambda f: (f.type != "CDS", -len(f.extract(record.seq))))
    seq = str(matches[0].extract(record.seq)).upper()
    if len(seq) < 300:
        raise ValueError(f"{row['taxon']} extracted {gene} sequence unexpectedly short")
    return seq


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


def _align_gene(records: dict[str, str], gene: str, workdir: Path) -> dict[str, str]:
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


def run_common_marker_audit(ledger_path: Path, output_path: Path, workdir: Path) -> dict:
    rows = load_accession_ledger(ledger_path)
    workdir.mkdir(parents=True, exist_ok=True)

    aligned_by_gene: dict[str, dict[str, str]] = {}
    fetched_lengths: dict[str, dict[str, int]] = {}
    for gene in GENES:
        sequences = {}
        for row in rows:
            seq = _fetch_gene(row, gene)
            sequences[row["taxon"]] = seq
            fetched_lengths.setdefault(row["taxon"], {})[gene] = len(seq)
            time.sleep(0.35)
        aligned_by_gene[gene] = _align_gene(sequences, gene, workdir)

    taxa = [row["taxon"] for row in rows]
    concatenated = {
        taxon: "".join(aligned_by_gene[gene][taxon] for gene in GENES)
        for taxon in taxa
    }
    concat_path = workdir / "ndhF_rbcL.aligned.fasta"
    _write_fasta(concatenated, concat_path)

    # Pairwise distances are descriptive only because historical accessions have
    # different sequence spans. Candidate ranking below uses one identical site
    # mask across the case and both candidates.
    distances: dict[str, dict[str, float | int]] = {}
    for i, a in enumerate(taxa):
        for b in taxa[i + 1 :]:
            distances[_pair_key(a, b)] = p_distance(concatenated[a], concatenated[b])

    comparisons = {
        case: compare_candidates_on_common_sites(concatenated, case)
        for case in CASE_TAXA
    }
    readout = {
        "analysis": "balance_u3_monochoria_common_marker_audit",
        "markers": list(GENES),
        "taxa": taxa,
        "fetched_lengths": fetched_lengths,
        "aligned_marker_lengths": {
            gene: len(next(iter(aligned_by_gene[gene].values())))
            for gene in GENES
        },
        "concatenated_alignment_length": len(next(iter(concatenated.values()))),
        "pairwise_distances_descriptive_only": distances,
        "candidate_comparisons_joint_site_mask": comparisons,
        "claim_ceiling": (
            "public_accession_ndhF_rbcL_joint_site_proximity_only_"
            "not_species_tree_not_pollination_evidence_not_historical_causation"
        ),
    }
    output_path.write_text(json.dumps(readout, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return readout


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    args = parser.parse_args()
    readout = run_common_marker_audit(args.ledger, args.output, args.workdir)
    print(json.dumps(readout, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
