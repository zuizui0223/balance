"""Fixture-only exact-origin provenance and controlled genetic-distance logic."""
from __future__ import annotations

from pathlib import Path
import pytest

from balance_domain.wurmbea_case2008_ndhf import (
    source_manifest, parse_fasta, pair_distance, analyze, run
)
from balance_domain.wurmbea_fitness_threshold import (
    analyze_thresholds, classify_advantage,
)


def test_case2008_manifest_all_population_terminals_protected():
    rows, digest = source_manifest()
    assert len(rows) == 22
    assert len(digest) == 64
    assert sum(x["sex_state"] == "M" for x in rows) == 12
    assert sum(x["sex_state"] == "D" for x in rows) == 10
    focal = {x["voucher"]: x for x in rows}
    assert {x["sex_state"] for x in (focal["MR1"], focal["MR3"])} == {"M","D"}
    assert {x["sex_state"] for x in (focal["AC53"], focal["AC38"])} == {"M","D"}
    assert focal["MR4"]["ndhf_accession"] == "EU044646"


def test_source_sequence_accession_header_and_lengths_are_strict():
    expected = "EU044643"
    header, seq = parse_fasta(
        f">ENA|{expected}|{expected}.1 Wurmbea biglandulosa ndhF\\n" + "ACGT"*130, expected
    )
    assert len(seq) == 520
    assert expected in header
    with pytest.raises(ValueError, match="pinned"):
        parse_fasta(">ENA|EU999999|EU999999.1 Wurmbea biglandulosa\\n" + "ACGT"*130, expected)
    with pytest.raises(ValueError, match="Wurmbea"):
        parse_fasta(">ENA|EU044643|EU044643.1 Animalia something\\n" + "ACGT"*130, expected)
    with pytest.raises(ValueError, match="short"):
        parse_fasta(f">ENA|{expected}|{expected}.1 Wurmbea\\nACGT", expected)


def test_ndhf_pairwise_alignment_handles_indel_and_ambiguous():
    a="A"*180+"C"*180+"G"*180
    b="A"*180+"C"*180+"G"*179+"T"
    got=pair_distance(a,b)
    assert got["comparable_aligned_ACGT_sites"] == 540
    assert got["aligned_ACGT_mismatches"] == 1
    assert abs(got["p_distance"]-1/540)<1e-12
    q=pair_distance("A"*500,"A"*250+"N"+"A"*249)
    assert q["excluded_ambiguous_site_pairs"] >= 1
    assert q["p_distance"] == 0
    assert pair_distance("A"*540, "A"*540)["p_distance"]==0


def test_complete_controlled_accession_replay_no_phylogenetic_origin(tmp_path):
    def fake_fetch(accession):
        dna = "A"*600 if accession != "EU044645" else "A"*599+"G"
        return f">ENA|{accession}|{accession}.1 Wurmbea control ndhF\\n{dna}"
    source=run(tmp_path,fetcher=fake_fetch)
    assert source["status"]=="VOUCHER_NDHF_METADATA_RECOVERED_NO_HISTORICAL_CAUSATION"
    assert source["ndhf_accessions_recovered"] == 22
    assert source["full_four_locus_phylogeny_replayed"] is False
    bg=source["focal_population_contrasts"]["Wurmbea biglandulosa subsp. biglandulosa"]
    assert bg["within_source_pairs_evaluated"] == 6
    assert bg["cross_sex_pairs_evaluated"] == 4
    d=source["focal_population_contrasts"]["Wurmbea dioica subsp. alba"]
    assert d["within_source_pairs_evaluated"] == 1
    assert d["cross_sex_pairs_evaluated"] == 1
    assert (tmp_path/"wurmbea_case2008_ndhf_source_receipt.json").exists()


def test_missing_accession_is_hold_not_false_negative(tmp_path):
    def fetch_with_one_missing(a):
        if a=="EU044634":
            raise ValueError("source temporarily unavailable")
        return f">ENA|{a}|{a}.1 Wurmbea control ndhF\\n"+("G"*650)
    report=run(tmp_path,fetcher=fetch_with_one_missing)
    assert report["status"]=="HOLD_INCOMPLETE_SEQUENCE_RECOVERY"
    assert report["ndhf_accessions_missing"]==["EU044634"]
    assert report["focal_population_contrasts"]["Wurmbea dioica subsp. alba"]["within_source_pairs_evaluated"]==0


def test_published_3_7_to_1_4_threshold_dependency_is_not_K_or_phi():
    result=analyze_thresholds()
    assert result["thresholds_for_a_strict_change_of_side"] == {
        "strictly_greater_than":1.4, "strictly_less_than":3.7,
    }
    nuclear=result["assumption_specific_results"]["SIMPLE_BIPARENTAL_NUCLEAR_TWOFOLD"]
    maternal=result["assumption_specific_results"]["STRICTLY_MATERNAL_NO_RESTORER_IDEALIZED_ONEFOLD"]
    assert nuclear["regime_classification_changes"] is True
    assert maternal["regime_classification_changes"] is False
    assert classify_advantage(1.4, 4.0) == "BELOW_ASSUMED_THRESHOLD"
    assert classify_advantage(1.4, 1.4) == "AT_ASSUMED_THRESHOLD"
    with pytest.raises(ValueError):
        classify_advantage(-1, 1)
    assert "independent new modular architecture construction or maintenance cost" in result["claims_that_are_not_identified"]
