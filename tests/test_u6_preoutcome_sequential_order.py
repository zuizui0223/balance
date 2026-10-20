"""Regression checks for all three source-first sequential visitor orders."""
from __future__ import annotations

import csv
import shutil
from pathlib import Path
import pytest

from balance_domain.u6_preoutcome_sequential_order import (
    ROOT, ORDER_LEDGER, SOURCE, PREDICTORS, ORIGINAL_PACKET, CODERS,
    analyze
)
from balance_domain.u6_preoutcome_common_support import (
    FREEZE, DEPENDENCE, TAXON,
)


def _copy_sources(to: Path) -> None:
    for rel in (
        FREEZE,SOURCE,PREDICTORS,DEPENDENCE,TAXON,CODERS,
        ORIGINAL_PACKET,ORDER_LEDGER
    ):
        destination=to/rel
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/rel,destination)


def _edit(to: Path,field: str,value: str,group="Crescentia_alata") -> None:
    path=to/ORDER_LEDGER
    with path.open(encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f)
        columns=reader.fieldnames
        rows=list(reader)
    next(x for x in rows if x["dependency_group"]==group)[field]=value
    with path.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def test_three_original_sources_are_ordered_two_early_one_late():
    v=analyze()
    assert v["status"]=="COMPLETE_SEQUENTIAL_STRATUM_SOURCE_REFINEMENT_NOT_ARCHITECTURE"
    assert v["source_roster"]=={
        "u6_admitted_groups":21,"timing_simultaneous":18,"timing_sequential":3,
    }
    assert v["original_source_directions"]=={
        "EFFECTIVE_TRANSFER_BEFORE_THEFT":1,
        "THEFT_BEFORE_EFFECTIVE_TRANSFER":2,
    }
    assert v["source_sequential_groups"]==[
        "Clusia_arrudae","Crescentia_alata","Tolmiea_menziesii"
    ]
    assert len(v["source_hashes"])==6
    assert all(len(value)==64 for value in v["source_hashes"].values())
    assert v["no_blinded_U6_architecture_coding_performed"] is True
    assert v["preoutcome_V4_anatomical_responses_read"] is False
    assert v["new_heritable_module_origin_established"] is False
    assert v["no_fitted_effect_or_p_value"] is True


def test_original_crescentia_nectar_is_not_mislabeled_pollen():
    r={x["dependency_group"]:x
       for x in analyze()["per_group_original_source_receipts"]}
    assert "NECTAR not pollen" in r["Crescentia_alata"]["source_effect_receipt"]
    assert "Four trees" in r["Crescentia_alata"]["source_effect_receipt"]
    assert "99%" in r["Clusia_arrudae"]["source_effect_receipt"]
    assert "0.1%" in r["Clusia_arrudae"]["source_effect_receipt"]
    assert "No per-visit" in r["Tolmiea_menziesii"]["source_effect_receipt"]
    assert all(row["direct_architecture_outcome"] is None for row in r.values())


def test_theft_pollination_order_cannot_be_swapped(tmp_path):
    _copy_sources(tmp_path)
    _edit(tmp_path,"refined_ordering","THEFT_BEFORE_EFFECTIVE_TRANSFER",
          "Tolmiea_menziesii")
    with pytest.raises(ValueError,match="sequence polarity"):
        analyze(tmp_path)


def test_nectar_percent_cannot_be_promoted_to_pollen_loss(tmp_path):
    _copy_sources(tmp_path)
    _edit(
        tmp_path,"quantitative_evidence_with_units",
        "Four trees; around 40% of pollen removed before bats",
    )
    with pytest.raises(ValueError,match="qualifier"):
        analyze(tmp_path)


def test_taxon_and_original_source_doi_locked_to_frozen_packets(tmp_path):
    _copy_sources(tmp_path)
    _edit(tmp_path,"source_doi","10.0000/incorrect")
    with pytest.raises(ValueError,match="matching original packet DOI"):
        analyze(tmp_path)


def test_source_timing_predicate_is_not_an_architecture_code(tmp_path):
    _copy_sources(tmp_path)
    _edit(tmp_path,"floral_architecture_inferred","SHARED")
    with pytest.raises(ValueError,match="cannot infer an anatomical outcome"):
        analyze(tmp_path)


def test_original_two_coder_outcomes_remain_blinded(tmp_path):
    _copy_sources(tmp_path)
    path=tmp_path/CODERS
    lines=path.read_text(encoding="utf-8")
    assert ",UNRESOLVED," in lines
    path.write_text(lines.replace(",UNRESOLVED,","SHARED,",1),encoding="utf-8")
    with pytest.raises(ValueError,match="pre-outcome audit must not open"):
        analyze(tmp_path)
