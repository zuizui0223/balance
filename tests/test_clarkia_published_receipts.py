"""Published-paper numeric receipts, not a raw Kay2020 experiment reanalysis."""
from __future__ import annotations

import json
from math import exp, isclose
import pytest

from balance_domain.clarkia_published_receipts import (
    analyze, ROOT, RECEIPT,
)


def test_primary_publication_numbers_recomputed_only_as_reported_ratios():
    r=analyze()
    assert r["source_original_study_programmes"] == 1
    assert r["status"] == "ORIGINAL_ARTICLE_SUMMARY_NOT_REANALYZED_DATA"
    assert r["published_compared_anther_timing_species"] == 11
    assert r["published_timing_phylo_p"] == .002
    assert r["published_no_detected_scopa_stigma_fate_difference_p"] == .17
    p=r["published_exposed_pollen"]
    assert p["dosing_mm"]==1.9
    assert p["no_dosing_mm"]==4.6
    assert isclose(p["no_dosing_over_dosing_ratio_computed"],4.6/1.9)
    a=r["published_stigma_delivery"]
    assert isclose(a["exponentiated_published_log_coefficient"],exp(-.3507))
    assert a["original_p"]==.27
    assert a["not_unconditionally_a_raw_count_ratio"] is True
    assert a["causal_effect_positive_certified"] is False
    assert a["strict_equivalence_certified"] is False
    assert r["raw_replicate_level_confidence_intervals_computed"] is False
    assert r["actual_developmental_origin_from_conflict_established"] is False
    assert r["source_raw_2018_pollen_trial_missing_in_public_manifest"] is True


def test_two_different_ecological_channels_are_never_equated_by_heteranthery():
    r=analyze()
    assert r["difference_between_whorl_morphology_and_ecological_role_identified_by_source_as_nonbijective"]
    assert "EVIDENCE_OF_TEMPORAL_POLLEN_PRESENTATION" in r["interpretation_support"]
    assert "BOTH_ANTHER_WHORLS_FUNCTIONALLY_EQUIVALENT_PROVED" in r["prohibited_claims"]
    assert "POLLEN_DOSING_CAUSALLY_INCREASED_STIGMA_DELIVERY_CONFIRMED" in r["prohibited_claims"]


def test_untrusted_source_changes_are_fail_closed(tmp_path):
    raw=json.loads((ROOT/RECEIPT).read_text())
    raw["provenance_status"]="RANDOMIZED_RAW_DATA_REANALYZED"
    altered=tmp_path/"payload.json"
    altered.write_text(json.dumps(raw))
    with pytest.raises(ValueError,match="provenance"):
        analyze(altered)


def test_corrupted_experimental_arrays_must_not_be_promoted(tmp_path):
    raw=json.loads((ROOT/RECEIPT).read_text())
    target=next(x for x in raw["receipts"] if x["id"]=="DOSE_EXPORTED_POLLEN")
    target["source_report"]["dosing_arrays"]=100
    altered=tmp_path/"payload.json"
    altered.write_text(json.dumps(raw))
    with pytest.raises(ValueError,match="unit denominators"):
        analyze(altered)


def test_reported_nonsignificance_cannot_be_claimed_as_equivalence(tmp_path):
    raw=json.loads((ROOT/RECEIPT).read_text())
    target=next(x for x in raw["receipts"] if x["id"]=="DOSE_EXPORTED_POLLEN")
    target["source_report"]["p"]=0.01
    altered=tmp_path/"payload.json"
    altered.write_text(json.dumps(raw))
    with pytest.raises(ValueError,match="equivalence"):
        analyze(altered)
