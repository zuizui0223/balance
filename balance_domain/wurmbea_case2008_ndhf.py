"""Voucher-level Wurmbea 2008 ndhF re-acquisition and descriptive sequence check.

Data: Case et al. 2008 IJPS 169:141-156 Table A1 (DOI 10.1086/523368).
Purpose: determine if original sex M/D vouchers have independently accessible
sequence records and compare within-taxon cpDNA differentiation. Do NOT
interpret cpDNA distance as selection, number/direction of historic
transitions, a species tree, nuclear sex determination, or structural payoff.

Only exact source vouchers and ndhF accessions are used. Source sequences are
recovered live from ENA/INSDC, and only hashes/lengths and results are saved.
"""
from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
from pathlib import Path
import re
from typing import Callable
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

SOURCE_DOI = "10.1086/523368"
SOURCE_PDF = "https://barrett.eeb.utoronto.ca/publications/files/2020/06/Case_et_al_IJPS169_141-156.pdf"
ENA_ENDPOINT = "https://www.ebi.ac.uk/ena/browser/api/fasta/{accession}?download=false"
MANIFEST_PATH = "data/WURMBEA_CASE_2008_TABLE_A1_NDHF_VOUCHERS.csv"
ALLOWED_STATES = {"M", "D"}
VALID_BASES = set("ACGTNRYKMSWBDHV")
FOCAL_GROUPS = {
    "Wurmbea biglandulosa subsp. biglandulosa": {"MR1", "MR2", "MR3", "MR4"},
    "Wurmbea dioica subsp. alba": {"AC53", "AC38"},
}
REPO_ROOT = Path(__file__).resolve().parents[1]


def source_manifest(base: Path = REPO_ROOT) -> tuple[list[dict[str, str]], str]:
    raw = (base / MANIFEST_PATH).read_bytes()
    rows = list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    expected = {
        "study_row", "taxon", "voucher", "sex_state", "ndhf_accession",
        "locality", "source_warning",
    }
    if len(rows) != 22 or set(rows[0]) != expected:
        raise ValueError("Expected all 22 original Australasian Table A1 vouchers")
    if sorted(int(r["study_row"]) for r in rows) != list(range(1, 23)):
        raise ValueError("Source rows not 1..22")
    for field in ("voucher", "ndhf_accession"):
        if len({r[field] for r in rows}) != len(rows):
            raise ValueError(f"Duplicate original {field}")
    if Counter(r["sex_state"] for r in rows) != {"M": 12, "D": 10}:
        raise ValueError("Unexpected published M/D state counts")
    for row in rows:
        accession = row["ndhf_accession"]
        if not re.fullmatch(r"(?:EU[0-9]{6}|AF[0-9]{6})", accession):
            raise ValueError("Unrecognized nucleotide source accession")
        if not row["taxon"].startswith("Wurmbea ") or not row["locality"]:
            raise ValueError("Table A1 botanical/sample identity missing")
    for taxon, ids in FOCAL_GROUPS.items():
        if {r["voucher"] for r in rows if r["taxon"] == taxon} != ids:
            raise ValueError(f"Focal original population sampling changed: {taxon}")
    return rows, hashlib.sha256(raw).hexdigest()


def fetch_ena(accession: str, *, timeout: int = 40) -> str:
    """Exact per-accession FASTA, not a genus/taxon keyword search."""
    request = Request(
        ENA_ENDPOINT.format(accession=accession),
        headers={"User-Agent": "balance-wurmbea-case2008-source-audit/1.0", "Accept": "text/plain"},
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8-sig")


def parse_fasta(fasta: str, accession: str) -> tuple[str, str]:
    rows = [s.strip() for s in fasta.splitlines() if s.strip()]
    if not rows or not rows[0].startswith(">"):
        raise ValueError(f"Non-FASTA original source response: {accession}")
    if sum(s.startswith(">") for s in rows) != 1:
        raise ValueError("One accession must yield exactly one sequence")
    header = rows[0]
    if not re.search(rf"(?<![A-Z0-9]){re.escape(accession)}(?:\.[0-9]+)?(?![0-9])", header, re.I):
        raise ValueError(f"Response not pinned to original accession {accession}")
    if "Wurmbea" not in header and "wurmbea" not in header.lower():
        raise ValueError(f"Expected Wurmbea named taxon in {accession}")
    seq = "".join(rows[1:]).upper()
    if len(seq) < 300 or any(base not in VALID_BASES for base in seq):
        raise ValueError(f"Invalid or unexpectedly short original ndhF sequence {accession}")
    return header, seq



def accession_voucher_header(header: str, expected_voucher: str) -> dict:
    """Compare the *deposited sequence* voucher to the printed Table A1 voucher.

    A verified GenBank accession is NOT a verified source-voucher identity.
    The exact MR2/MR3 psbBTNH discrepancy is held, never silently swapped.
    """
    m = re.search(r"\\bvoucher\\s+M\\.\\s*Ramsey\\s+(\\d+)\\b", header, re.I)
    a = re.search(r"\\bvoucher\\s+A\\.\\s*Case\\s+(\\d+)\\b", header, re.I)
    observed = ("MR" + m.group(1)) if m else (("AC" + a.group(1)) if a else None)
    return {
        "expected_source_voucher": expected_voucher,
        "archive_voucher": observed,
        "status": (
            "MATCHED_SOURCE_VOUCHER" if observed == expected_voucher
            else ("ARCHIVE_VOUCHER_UNSPECIFIED" if observed is None
                  else "HOLD_ARCHIVE_SOURCE_VOUCHER_CONFLICT")
        ),
    }



def pair_distance(seq_a: str, seq_b: str) -> dict:
    """Global pairwise alignment with explicitly defined gapping; descriptive only.

    Biopython is installed in the source execution environment, never silently
    substitutes unaligned zipped string comparisons.
    """
    from Bio.Align import PairwiseAligner

    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.match_score = 1.0
    aligner.mismatch_score = -1.0
    aligner.open_gap_score = -5.0
    aligner.extend_gap_score = -0.5
    ali = aligner.align(seq_a, seq_b)[0]
    segments_a, segments_b = ali.aligned
    comparable = 0
    different = 0
    ambiguous = 0
    for (a1, a2), (b1, b2) in zip(segments_a, segments_b):
        if a2 - a1 != b2 - b1:
            raise ValueError("Pairwise alignment blocks have unequal lengths")
        for x, y in zip(seq_a[a1:a2], seq_b[b1:b2]):
            if x not in "ACGT" or y not in "ACGT":
                ambiguous += 1
                continue
            comparable += 1
            different += x != y
    return {
        "comparable_aligned_ACGT_sites": comparable,
        "aligned_ACGT_mismatches": different,
        "excluded_ambiguous_site_pairs": ambiguous,
        "p_distance": different / comparable if comparable >= 300 else None,
        "minimum_comparable_sites_gate": 300,
        "alignment_method": "Biopython global PairwiseAligner match=1 mismatch=-1 gap_open=-5 gap_extend=-0.5",
    }


def analyze(
    entries: list[dict[str, str]],
    sequences: dict[str, str],
) -> dict:
    missing = [r["ndhf_accession"] for r in entries if r["ndhf_accession"] not in sequences]
    focus = {}
    for group, expected in FOCAL_GROUPS.items():
        rows = [r for r in entries if r["voucher"] in expected]
        distances = []
        for i, first in enumerate(rows):
            for second in rows[i + 1:]:
                if first["ndhf_accession"] not in sequences or second["ndhf_accession"] not in sequences:
                    continue
                d = pair_distance(
                    sequences[first["ndhf_accession"]],
                    sequences[second["ndhf_accession"]],
                )
                distances.append({
                    "vouchers": [first["voucher"], second["voucher"]],
                    "sex_states": [first["sex_state"], second["sex_state"]],
                    "sex_state_differs": first["sex_state"] != second["sex_state"],
                    "pairwise_ndhF": d,
                })
        focus[group] = {
            "registered_vouchers": len(rows),
            "registered_states": dict(Counter(r["sex_state"] for r in rows)),
            "within_source_pairs_evaluated": len(distances),
            "cross_sex_pairs_evaluated": sum(d["sex_state_differs"] for d in distances),
            "pair_details": distances,
            "inferential_unit": "vouchers/populations, not independent phylogenetic transitions",
        }
    return {
        "status": "VOUCHER_NDHF_METADATA_RECOVERED_NO_HISTORICAL_CAUSATION" if not missing else "HOLD_INCOMPLETE_SEQUENCE_RECOVERY",
        "ndhf_accessions_expected": len(entries),
        "ndhf_accessions_recovered": len(sequences),
        "ndhf_accessions_missing": sorted(missing),
        "study_sex_state_vouchers": dict(Counter(r["sex_state"] for r in entries)),
        "source": {"doi": SOURCE_DOI, "table": "A1", "marker": "chloroplast ndhF"},
        "focal_population_contrasts": focus,
        "prohibited_claims": [
            "one plastid locus is a species or nuclear sex-determination tree",
            "observed M/D sample pairing is an evolutionary transition count",
            "different cpDNA haplotypes identify selection for structural modularity",
            "pairwise distances identify ancestral transition directions",
            "these data quantify K, Phi, male reproductive payoff, or total fitness",
        ],
    }


def run(
    output_dir: Path,
    *,
    base: Path = REPO_ROOT,
    fetcher: Callable[[str], str] = fetch_ena,
) -> dict:
    rows, source_sha = source_manifest(base)
    sequences: dict[str, str] = {}
    records = []
    failures = []
    # Parallel bounded ENA requests; source membership frozen before query.
    with ThreadPoolExecutor(max_workers=4) as pool:
        tasks = {
            r["ndhf_accession"]: pool.submit(fetcher, r["ndhf_accession"])
            for r in rows
        }
        for r in rows:
            accession = r["ndhf_accession"]
            try:
                header, seq = parse_fasta(tasks[accession].result(), accession)
                identity = accession_voucher_header(header, r["voucher"])
                if identity["status"] == "HOLD_ARCHIVE_SOURCE_VOUCHER_CONFLICT":
                    raise ValueError(
                        "GenBank voucher differs from published Table A1: "
                        + str(identity)
                    )
                sequences[accession] = seq
                records.append({
                    "accession": accession, "voucher": r["voucher"],
                    "archive_voucher_check": identity,
                    "header": header, "sequence_length": len(seq),
                    "sequence_sha256": hashlib.sha256(seq.encode()).hexdigest(),
                })
            except (HTTPError, URLError, ValueError, UnicodeError, TimeoutError, OSError) as error:
                failures.append({
                    "accession": accession,
                    "failure_type": type(error).__name__,
                    "reason": str(error)[:300],
                })

    result = analyze(rows, sequences)
    result.update({
        "schema": "BALANCE_WURMBEA_CASE2008_GENBANK_NDHF_V1",
        "source_manifest_sha256": source_sha,
        "verified_records": records,
        "archive_voucher_matched": sum(
            x["archive_voucher_check"]["status"] == "MATCHED_SOURCE_VOUCHER"
            for x in records
        ),
        "archive_voucher_unspecified": [
            x["accession"] for x in records
            if x["archive_voucher_check"]["status"] == "ARCHIVE_VOUCHER_UNSPECIFIED"
        ],
        "failed_accessions": failures,
        "observational_cohort_definition": "original 22 Australasian Case 2008 vouchers with categorical source-coded M/D states",
        "full_four_locus_phylogeny_replayed": False,
        "unrooted_single_locus_only": True,
        "source_public_sequences_redistributed": False,
    })
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "wurmbea_case2008_ndhf_source_receipt.json"
    with target.open("x", encoding="utf-8") as file:
        json.dump(result, file, indent=2, sort_keys=True)
        file.write("\n")
    return result
