"""Voucher-linked four-locus source replay for six sex-polymorphic Wurmbea tips.

This is a bounded data-coverage and matched cpDNA sequence observation, not
a four-locus inferred species tree or historical/causal origin reconstruction.
The MR4 trnLF entry is genuinely absent from Case et al. (2008) Table A1.
"""
from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from typing import Callable

from .wurmbea_case2008_ndhf import (
    REPO_ROOT, fetch_ena, parse_fasta, pair_distance, source_manifest
)

FOUR_LOCUS_PATH = "data/WURMBEA_CASE_2008_FOCAL_FOUR_LOCUS_VOUCHERS.csv"
LOCUS_NAMES = ("ndhf", "atpb_rbcl", "trnlf", "psbb_tnh")
POPULATION_GROUPS = {
    "Wurmbea_biglandulosa_subsp_biglandulosa": ("MR1","MR2","MR3","MR4"),
    "Wurmbea_dioica_subsp_alba": ("AC53","AC38"),
}


def read_focal_manifest(base: Path = REPO_ROOT) -> tuple[list[dict[str, str]], str]:
    path = base / FOUR_LOCUS_PATH
    blob = path.read_bytes()
    rows = list(csv.DictReader(blob.decode("utf-8-sig").splitlines()))
    expected = {"voucher", "sex_state", *LOCUS_NAMES, "source_missing_note"}
    if len(rows) != 6 or set(rows[0]) != expected:
        raise ValueError("Source Table A1 requires exactly six focal population terminals")
    if {r["voucher"] for r in rows} != set(sum((list(x) for x in POPULATION_GROUPS.values()), [])):
        raise ValueError("Unexpected focal voucher identity")
    base_rows,_ = source_manifest(base)
    ndhf_registry = {r["voucher"]:(r["ndhf_accession"],r["sex_state"]) for r in base_rows}
    names = []
    for row in rows:
        if (row["ndhf"],row["sex_state"]) != ndhf_registry[row["voucher"]]:
            raise ValueError("Four-locus ledger changed original source voucher/ndhF/sexual state")
        for locus in LOCUS_NAMES:
            if row[locus]:
                names.append(row[locus])
    if len(names) != 23 or len(names) != len(set(names)):
        raise ValueError("Original six-voucher source 23 locus-accession identities changed")
    missing = [(r["voucher"],r["source_missing_note"]) for r in rows if not r["trnlf"]]
    if missing != [("MR4","No_trnLF_accession_in_Table_A1")]:
        raise ValueError("Only MR4 may omit original trnLF accession")
    return rows, hashlib.sha256(blob).hexdigest()


def contrast_pairs(rows: list[dict[str, str]], sequences: dict[str, str]) -> dict:
    groups = {}
    for key, voucher_ids in POPULATION_GROUPS.items():
        group_rows = [r for r in rows if r["voucher"] in voucher_ids]
        pairs = []
        for i, x in enumerate(group_rows):
            for y in group_rows[i + 1:]:
                loci = {}
                for locus in LOCUS_NAMES:
                    if not x[locus] or not y[locus]:
                        loci[locus] = {
                            "status":"SOURCE_MISSING_LOCUS_ACCESSION",
                            "compared":False
                        }
                        continue
                    if x[locus] not in sequences or y[locus] not in sequences:
                        loci[locus] = {
                            "status":"HOLD_MISSING_VERIFIED_SEQUENCE",
                            "compared":False
                        }
                        continue
                    d = pair_distance(sequences[x[locus]],sequences[y[locus]])
                    loci[locus] = {"status":"COMPARED" if d["p_distance"] is not None
                                   else "HOLD_INSUFFICIENT_SITES",
                                   "compared":d["p_distance"] is not None,
                                   "p_distance":d["p_distance"],
                                   "comparable_sites":d["comparable_aligned_ACGT_sites"],
                                   "mismatches":d["aligned_ACGT_mismatches"]}
                good = [d for d in loci.values() if d["compared"]]
                pairs.append({
                    "vouchers": [x["voucher"],y["voucher"]],
                    "source_states":[x["sex_state"],y["sex_state"]],
                    "source_states_differ":x["sex_state"]!=y["sex_state"],
                    "loci":loci,
                    "complete_all_four_loci":len(good)==4,
                    "compared_loci":len(good),
                    "total_pairwise_aligned_comparable_sites":sum(d["comparable_sites"] for d in good),
                    "total_pairwise_mismatches":sum(d["mismatches"] for d in good),
                    "observed_identity_across_all_compared_loci":(
                        bool(good) and all(d["mismatches"]==0 for d in good)
                    ),
                    "missing_marker_is_not_assumed_identical":True,
                })
        groups[key] = {
            "source_vouchers":list(voucher_ids),
            "source_M_D":dict(Counter(r["sex_state"] for r in group_rows)),
            "opposite_state_pairs":sum(p["source_states_differ"] for p in pairs),
            "pairwise_descriptions":pairs,
        }
    return groups


def run(
    output_dir: Path,
    *,
    base: Path = REPO_ROOT,
    fetcher: Callable[[str],str] = fetch_ena,
) -> dict:
    rows, sha = read_focal_manifest(base)
    pairs = [(r["voucher"],l,r[l]) for r in rows for l in LOCUS_NAMES if r[l]]
    seqs = {}
    records = []
    failures = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        tasks={acc:pool.submit(fetcher,acc) for _,_,acc in pairs}
        for voucher,locus,acc in pairs:
            try:
                header,seq=parse_fasta(tasks[acc].result(),acc)
                seqs[acc]=seq
                records.append({
                    "voucher":voucher,"locus":locus,"accession":acc,
                    "length":len(seq),"sequence_sha256":hashlib.sha256(seq.encode()).hexdigest(),
                    "original_archive_header":header,
                })
            except (HTTPError,URLError,OSError,TimeoutError,UnicodeError,ValueError) as e:
                failures.append({
                    "voucher":voucher,"locus":locus,"accession":acc,
                    "error":type(e).__name__,"message":str(e)[:220],
                })
    results = contrast_pairs(rows,seqs)
    state="FOCAL_MULTILOCUS_SOURCE_VERIFIED_DESCRIPTIVE_ONLY" if len(seqs)==23 else "HOLD_INCOMPLETE_FOCAL_MULTILOCUS_SOURCE"
    report = {
        "schema":"BALANCE_WURMBEA_CASE2008_FOCAL_4LOCUS_V1",
        "status":state,
        "source":"Case et al. (2008), IJPS Table A1, DOI 10.1086/523368",
        "focal_manifest_sha256":sha,
        "source_unique_accessions_expected":23,
        "accessions_verified":len(seqs),
        "accessions_failed":failures,
        "original_table_missing_marker":"MR4:trnLF",
        "focal_groups":results,
        "verified_record_metadata":records,
        "no_phylogenetic_tree_estimated":True,
        "no_ancestral_transition_counts_estimated":True,
        "no_nuclear_evidence":True,
        "single_plastid_haplotype_genealogy_not_species_phylogeny":True,
        "sequence_bytes_redistributed":False,
    }
    output_dir.mkdir(parents=True,exist_ok=True)
    with (output_dir/"wurmbea_case2008_focal_four_locus_readout.json").open("x",encoding="utf-8") as f:
        json.dump(report,f,indent=2,sort_keys=True)
        f.write("\n")
    return report
