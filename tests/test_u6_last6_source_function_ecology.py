"""Last 6 preselected U6 original ecological source histories; no V4 response."""
from __future__ import annotations

import csv
import shutil
import pytest

from balance_domain.u6_last6_source_function_ecology import (
    ROOT,FREEZE,PACKET,PREDICTORS,PILOT,NEXT6,
    DEPENDENCE,CODER,LAST6,analyze,
)


def copied_sources(tmp_path):
    for path in (FREEZE,PACKET,PREDICTORS,PILOT,NEXT6,DEPENDENCE,CODER,LAST6):
        dest=tmp_path/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/path,dest)


def alter(path,change):
    with path.open(newline="",encoding="utf-8") as h:
        reader=csv.DictReader(h)
        fields=list(reader.fieldnames or ())
        rows=list(reader)
    change(rows)
    with path.open("w",newline="",encoding="utf-8") as h:
        writer=csv.DictWriter(h,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_last_six_actual_source_provenance_and_provisional_bookkeeping():
    z=analyze()
    assert z["frozen_taxon_groups"]==21
    assert z["original_source_timing"]=={"simultaneous":18,"sequential":3}
    assert z["final_six_original_source_selected"]==[
        "Nothofagus_pumilio","Passiflora_foetida","Prockia_crucis",
        "Pseudobombax_ellipticum","Theobroma_cacao","Zea_mays",
    ]
    assert z["main_plus_stacked_ecology_taxa"]==18
    assert z["main_plus_stacked_groups_not_in_this_branch"]==[
        "Banksia_menziesii","Bromelia_antiacantha","Campanula_americana",
    ]
    assert z["cross_branch_provisional_distinct_source_taxa"]==21
    assert z["cross_branch_provisional_not_canonical"] is True
    assert z["original_independent_coder_slots"]==42
    assert z["independently_completed_architecture_slots"]==0
    assert z["original_V4_confirmatory_architecture_opened"] is False
    assert z["original_source_inclusion_modified"] is False
    assert z["genetically_evolved_new_module_origins_demonstrated"] is False
    assert all(len(x)==64 for x in z["source_sha256"].values())


def test_wind_pollen_predator_food_does_not_demonstrate_causal_emasculation():
    z=analyze()
    assert z["zeamays_pollen_predator_food_without_plant_fitness_source_review_required"]
    records={x["dependency_group"]:x for x in z["new_observation_records"]}
    assert records["Zea_mays"]["functional_location"]==(
        "WIND_DISPERSED_POLLEN_AS_DIET_OF_PREDATORY_BEETLES"
    )
    assert "ADMISSION_ELIGIBILITY_REVIEW_REQUIRED" in (
        records["Zea_mays"]["source_adjudication_status"]
    )
    assert records["Passiflora_foetida"]["functional_location"]==(
        "SOURCE_ANTHER_POLLEN_AND_STIGMA_CONTACT_DIFFER"
    )
    assert records["Theobroma_cacao"]["admission_reference_id"]==(
        "U6_REF_153;U6_REF_155"
    )


def test_zea_pollen_beetle_diet_source_cannot_be_promoted_to_plant_fitness(tmp_path):
    copied_sources(tmp_path)
    def edit(rows):
        next(x for x in rows if x["dependency_group"]=="Zea_mays")[
            "functional_location"
        ]="SOURCE_ANTHER_POLLEN_SOLE_FLORAL_REWARD"
    alter(tmp_path/LAST6,edit)
    with pytest.raises(ValueError,match="Zea predatory beetle pollen-diet"):
        analyze(tmp_path)


def test_source_extractor_is_not_independent_architecture_coder(tmp_path):
    copied_sources(tmp_path)
    def edit(rows):
        rows[0]["formal_u6_architecture_assigned"]="STRUCTURAL_MODULE_DIVISION"
    alter(tmp_path/LAST6,edit)
    with pytest.raises(ValueError,match="may not fill"):
        analyze(tmp_path)
    copied_sources(tmp_path)
    def coder(rows):
        rows[0]["architecture_mode"]="SHARED"
        rows[0]["coding_status"]="COMPLETED"
    alter(tmp_path/CODER,coder)
    with pytest.raises(ValueError,match="NOT opened"):
        analyze(tmp_path)


def test_missing_source_evidence_is_not_rewritten_as_confirmed(tmp_path):
    copied_sources(tmp_path)
    def edit(rows):
        target=next(x for x in rows if x["dependency_group"]=="Prockia_crucis")
        target["source_adjudication_status"]="FULL_EXPERIMENT_REPLAYED"
    alter(tmp_path/LAST6,edit)
    with pytest.raises(ValueError,match="Primary-source evidence ceilings"):
        analyze(tmp_path)


def test_last_six_admission_reference_must_match_frozen_source(tmp_path):
    copied_sources(tmp_path)
    def edit(rows):
        target=next(x for x in rows if x["dependency_group"]=="Theobroma_cacao")
        target["admission_reference_id"]="U6_REF_155"
    alter(tmp_path/LAST6,edit)
    with pytest.raises(ValueError,match="Original admission reference"):
        analyze(tmp_path)


def test_preselected_last_six_source_timing_must_not_be_changed(tmp_path):
    copied_sources(tmp_path)
    def edit(rows):
        target=next(x for x in rows if x["cluster_id"]=="Nothofagus_pumilio"
                    and x["predictor"]=="conflict_timing_geometry")
        target["reported_value"]="SEQUENTIAL_WITHIN_UNIT"
    alter(tmp_path/PREDICTORS,edit)
    with pytest.raises(ValueError,match="Original source timing denominator"):
        analyze(tmp_path)


def test_cannot_fill_morphological_lookalike_as_new_structural_origin(tmp_path):
    copied_sources(tmp_path)
    def edit(rows):
        row=next(x for x in rows if x["dependency_group"]=="Passiflora_foetida")
        row["independent_coder_authorship"]="CODER_B"
    alter(tmp_path/LAST6,edit)
    with pytest.raises(ValueError,match="coder authorship"):
        analyze(tmp_path)
