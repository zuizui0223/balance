"""Unpooled original-source evidence for morphology/non-bijective function mechanisms."""
from __future__ import annotations
import json
import shutil
from pathlib import Path
import pytest

from balance_domain.pollen_architecture_mechanism_crosscheck import (
    analyze, ROOT, U3, DEP, CLARKIA_SOURCE,
)


def test_real_ten_taxa_four_dependence_blocks_preserve_distinct_routing():
    r=analyze()
    assert r["status"]=="SELECTED_SOURCE_FUNCTIONAL_NONBIJECTION_NOT_MACRO_EFFECT"
    assert r["distinct_source_taxa"]==10
    assert r["u3_taxon_rows"]==8
    assert r["u3_pass_pairs"]==4
    assert r["u3_taxonomic_dependence_blocks"]==3
    assert r["clarkia_independent_original_papers"]==1
    assert r["dependence_blocks_in_combined_selected_comparison"]==4
    assert r["visible_heteranthery_cases"]==6
    assert r["no_visible_heteranthery_controls"]==4
    assert r["selected_morphology_by_mechanism"]=={
        "NO_VISIBLE_HETERANTHERY":{
            "ROLE_DIVISION_AMONG_FLOWERS":1,
            "ROLE_DIVISION_WITHIN_FLOWER":1,
            "UNRESOLVED":2,
        },
        "VISIBLE_HETERANTHERY":{
            "ROLE_DIVISION_WITHIN_FLOWER":4,
            "TEMPORAL_POLLEN_DOSING_SOURCE_FAVORED":2,
        },
    }
    assert all(r["constructive_morphology_nonidentifiability"].values())
    assert r["not_independent_taxon_macro_prevalence"] is True
    assert r["no_identified_same_axis_conflict_loss"] is True
    assert r["no_genetically_inherited_transition_or_historical_causality"] is True
    assert r["provenance"]["clarkia_raw_source_effects_recomputed"] is False


def test_same_morphology_yields_different_functions_and_vice_versa():
    taxa={r["taxon"]:r for r in analyze()["selected_taxon_evidence_rows"]}
    assert taxa["Solanum rostratum"]["visible_morphology"]==taxa["Clarkia cylindrica"]["visible_morphology"]
    assert taxa["Solanum rostratum"]["functional_mechanism"]!=taxa["Clarkia cylindrica"]["functional_mechanism"]
    assert taxa["Senna alata"]["functional_mechanism"]==taxa["Senna spectabilis"]["functional_mechanism"]
    assert taxa["Senna alata"]["visible_morphology"]!=taxa["Senna spectabilis"]["visible_morphology"]
    assert taxa["Solanum lycocarpum"]["functional_mechanism"]=="ROLE_DIVISION_AMONG_FLOWERS"
    assert taxa["Senna covesii"]["functional_mechanism"]=="UNRESOLVED"
    assert taxa["Osbeckia chinensis"]["pollen_fate_source_status"]=="UNRESOLVED"
    assert taxa["Clarkia unguiculata"]["pollen_fate_source_status"].endswith("NO_DIRECT_WHORL_FATE_TEST")


def _copy(tmp_path):
    for rel in (U3,DEP,str(CLARKIA_SOURCE)):
        src=ROOT/rel
        dest=tmp_path/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dest)


def test_missing_clarkia_raw_receipts_are_never_promoted(tmp_path):
    _copy(tmp_path)
    p=tmp_path/str(CLARKIA_SOURCE)
    raw=json.loads(p.read_text())
    raw["source_data_raw_access_status"]="RAW_REPLAY_COMPLETED"
    p.write_text(json.dumps(raw))
    with pytest.raises(ValueError,match="published-only"):
        analyze(tmp_path)


def test_unresolved_u3_control_is_not_inferred_shared_or_conflict_free(tmp_path):
    _copy(tmp_path)
    p=tmp_path/U3
    text=p.read_text()
    assert "Senna covesii,UNRESOLVED," in text
    p.write_text(text.replace("Senna covesii,UNRESOLVED,",
                              "Senna covesii,WITHIN_FLOWER_DIVISION_OF_LABOUR,",1))
    with pytest.raises(ValueError,match="Unresolved source case"):
        analyze(tmp_path)


def test_u3_matched_phylogenetic_dependence_is_not_lost(tmp_path):
    _copy(tmp_path)
    p=tmp_path/DEP
    raw=p.read_text()
    assert "U3_DEP_SENNA_01" in raw
    p.write_text(raw.replace("U3_DEP_SENNA_01","U3_DEP_FAKE_SPLIT_01",1))
    with pytest.raises(ValueError,match="dependence blocks"):
        analyze(tmp_path)


def test_published_nonsignificant_clarkia_pollen_fate_stays_unknown(tmp_path):
    _copy(tmp_path)
    p=tmp_path/str(CLARKIA_SOURCE)
    raw=json.loads(p.read_text())
    rec=next(r for r in raw["receipts"] if r["id"]=="POLLEN_FATE_CYLINDRICA")
    rec["source_report"]["p"]=0.01
    p.write_text(json.dumps(raw))
    with pytest.raises(ValueError,match="Cannot promote"):
        analyze(tmp_path)
