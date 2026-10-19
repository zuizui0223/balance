"""Bounded four-source-locus population contrast tests; no historical claim."""
from __future__ import annotations

from balance_domain.wurmbea_case2008_four_locus import (
    read_focal_manifest, contrast_pairs, run, LOCUS_NAMES
)


def test_original_focal_four_locus_table_and_genuine_missingness():
    rows,sha=read_focal_manifest()
    assert len(rows)==6 and len(sha)==64
    assert tuple(LOCUS_NAMES)==("ndhf","atpb_rbcl","trnlf","psbb_tnh")
    mr4=next(r for r in rows if r["voucher"]=="MR4")
    assert mr4["ndhf"]=="EU044646"
    assert mr4["atpb_rbcl"]=="EU044620"
    assert mr4["trnlf"]==""
    assert mr4["psbb_tnh"]=="EU044682"
    assert next(r for r in rows if r["voucher"]=="AC38")["sex_state"]=="D"


def test_locus_absence_not_imputed_even_with_identical_sequences():
    rows,_=read_focal_manifest()
    seqs={r[l]:"A"*600 for r in rows for l in LOCUS_NAMES if r[l]}
    summary=contrast_pairs(rows,seqs)
    bg=summary["Wurmbea_biglandulosa_subsp_biglandulosa"]
    assert bg["opposite_state_pairs"]==4
    pairs={tuple(p["vouchers"]):p for p in bg["pairwise_descriptions"]}
    p=pairs[("MR2","MR4")]
    assert p["loci"]["trnlf"]["status"]=="SOURCE_MISSING_LOCUS_ACCESSION"
    assert p["compared_loci"]==3
    assert p["total_pairwise_aligned_comparable_sites"]==1800
    assert p["observed_identity_across_all_compared_loci"] is True
    assert p["complete_all_four_loci"] is False
    assert p["missing_marker_is_not_assumed_identical"]
    q=summary["Wurmbea_dioica_subsp_alba"]["pairwise_descriptions"][0]
    assert q["compared_loci"]==4
    assert q["complete_all_four_loci"] is True


def _accession_voucher_map():
    rows,_=read_focal_manifest()
    return {r[l]:r["voucher"] for r in rows for l in LOCUS_NAMES if r[l]}


def _archive_voucher_name(v):
    return "M. Ramsey "+v[2:] if v.startswith("MR") else "A. Case "+v[2:]


def test_original_source_candidate_regression_explicit_mismatch(tmp_path):
    mapping=_accession_voucher_map()
    def fake(acc):
        seq="C"*550 if acc!="EU044681" else "C"*549+"A"
        ident=_archive_voucher_name(mapping[acc])
        return f">ENA|{acc}|{acc}.1 Wurmbea voucher {ident} comparative plastid region\n{seq}"
    r=run(tmp_path,fetcher=fake)
    assert r["status"]=="FOCAL_MULTILOCUS_SOURCE_VERIFIED_DESCRIPTIVE_ONLY"
    assert r["accessions_verified"]==23
    assert r["source_unique_accessions_expected"]==23
    assert r["no_ancestral_transition_counts_estimated"]
    assert not r["sequence_bytes_redistributed"]
    group=r["focal_groups"]["Wurmbea_biglandulosa_subsp_biglandulosa"]
    pairs={tuple(x["vouchers"]):x for x in group["pairwise_descriptions"]}
    assert pairs[("MR2","MR4")]["total_pairwise_mismatches"]==1
    assert pairs[("MR2","MR4")]["compared_loci"]==3
    assert (tmp_path/"wurmbea_case2008_focal_four_locus_readout.json").exists()


def test_missing_source_sequence_blocks_completeness(tmp_path):
    mapping=_accession_voucher_map()
    def fetch(acc):
        if acc=="EU044681":
            raise ValueError("source temporarily missing")
        ident=_archive_voucher_name(mapping[acc])
        return f">ENA|{acc}|{acc}.1 Wurmbea voucher {ident} plastid gene\n"+("T"*550)
    r=run(tmp_path,fetcher=fetch)
    assert r["status"]=="HOLD_INCOMPLETE_FOCAL_MULTILOCUS_SOURCE"
    assert len(r["accessions_failed"])==1
    assert r["accessions_failed"][0]["accession"]=="EU044681"
    pair=next(p for p in r["focal_groups"]["Wurmbea_biglandulosa_subsp_biglandulosa"]["pairwise_descriptions"]
              if p["vouchers"]==["MR2","MR4"])
    assert pair["loci"]["psbb_tnh"]["status"]=="HOLD_MISSING_VERIFIED_SEQUENCE"
    assert pair["complete_all_four_loci"] is False


def test_real_case_table_archive_MR2_MR3_swap_is_held_not_silent(tmp_path):
    mapping=_accession_voucher_map()
    def source_for(acc):
        actual=mapping[acc]
        if acc=="EU044681":
            actual="MR3"
        if acc=="EU044680":
            actual="MR2"
        ident=_archive_voucher_name(actual)
        return f">ENA|{acc}|{acc}.1 Wurmbea voucher {ident} plastid gene\n"+("T"*550)
    report=run(tmp_path,fetcher=source_for)
    assert report["status"] == "SOURCE_TABLE_ARCHIVE_DISCORDANCE_HELD"
    assert report["fasta_accessions_downloaded"]==23
    assert report["exact_source_voucher_identity_matches"]==21
    assert set(x["accession"] for x in report["source_voucher_conflicts_held"])=={
        "EU044681","EU044680",
    }
    strict=report["focal_groups"]["Wurmbea_biglandulosa_subsp_biglandulosa"]
    focus=next(x for x in strict["pairwise_descriptions"] if x["vouchers"]==["MR2","MR4"])
    assert focus["compared_loci"]==2
    assert focus["loci"]["psbb_tnh"]["status"]=="HOLD_MISSING_VERIFIED_SEQUENCE"
    alt=report["genbank_voucher_assignment_sensitivity"]
    assert alt["status"]=="POSTOPEN_ARCHIVE_VOUCHER_ASSIGNMENT_SENSITIVITY_NOT_PRIMARY"
    adjusted=alt["focal_groups"]["Wurmbea_biglandulosa_subsp_biglandulosa"]
    focus2=next(x for x in adjusted["pairwise_descriptions"] if x["vouchers"]==["MR2","MR4"])
    assert focus2["compared_loci"]==3
