"""Claim and transcription guards for one published 2007 floral study."""
import csv
import importlib.util
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/audit_pitcairnia_2007_role_duality.py'
spec=importlib.util.spec_from_file_location('audit_pitcairnia_role',SCRIPT)
audit_module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)

def test_original_single_programme_totals_and_behavior():
    a=audit_module.audit()
    s=a['source']
    assert (s['plant_species_count'],s['primary_study_count'],s['patches_observed'],s['plants_observed'])==(1,1,6,60)
    x=a['source_descriptive_visit_counts']
    assert (x['total_visits'],x['robber_behavior_visits'],x['robber_species_with_source_reported_stigma_pollen_visits'])==(1146,697,664)
    assert x['robber_behavior_visits_fraction']==pytest.approx(697/1146)
    assert a['visitor_species']['Coereba flaveola']['reported_stigma_pollen_evidence']=='detected'
    assert a['visitor_species']['Chlorostilbon maugaeus']['reported_stigma_pollen_evidence']=='not_distinguishable_from_control'

def test_no_function_fitness_or_independent_species_inference():
    a=audit_module.audit()
    assert all(a['interpretation_guards'].values())
    assert a['source']['source_status'].startswith('human_transcribed')
    assert a['visitor_species']['Coereba flaveola']['approx_relative_pollen_load_per_single_visit']==pytest.approx(.067)

def copy_source(tmp_path):
    dst=tmp_path/'source.csv'
    with audit_module.SOURCE.open(newline='',encoding='utf-8') as f:rows=list(csv.DictReader(f))
    return dst,rows

def write_source(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def test_wrongly_classifying_primary_robber_as_nonpollinating_fails(tmp_path):
    path,rows=copy_source(tmp_path)
    next(x for x in rows if x['visitor_species']=='Coereba flaveola')['pollen_load_evidence']='not_distinguishable_from_control'
    write_source(path,rows)
    with pytest.raises(ValueError,match='role, count or reported'):
        audit_module.audit(path)

def test_changed_denominator_or_duplicate_visitor_fails(tmp_path):
    path,rows=copy_source(tmp_path)
    next(x for x in rows if x['visitor_species']=='Coereba flaveola')['total_observed_visits']='665'
    write_source(path,rows)
    with pytest.raises(ValueError,match='role, count or reported'):
        audit_module.audit(path)
    rows[0]['visitor_species']=rows[1]['visitor_species']
    write_source(path,rows)
    with pytest.raises(ValueError,match='unique visitor'):
        audit_module.audit(path)
