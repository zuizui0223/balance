#!/usr/bin/env python3
"""Exploratory Zurich cross-plant guild-composition proxy diagnostic.

The original EnviDat source is SHA256 verified by the Zurich upstream audit.
Sharing a garden prevents interpretation as a randomized negative control.
No BALANCE V4 independent architecture outcomes are accessed.
"""
from __future__ import annotations
import argparse
import importlib.util
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
UPSTREAM=ROOT/"scripts/analyze_zurich_four_species.py"

def upstream():
    spec=importlib.util.spec_from_file_location("zurich_original_source",UPSTREAM)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def independent_loo(y,X):
    import numpy as np
    if np.linalg.matrix_rank(X)!=X.shape[1]:
        raise ValueError("Full crossplant design not estimable")
    errors=[]
    for j in range(len(y)):
        train=np.arange(len(y))!=j
        if np.linalg.matrix_rank(X[train])!=X.shape[1]:
            raise ValueError("Held-out crossplant design not estimable")
        beta=np.linalg.lstsq(X[train],y[train],rcond=None)[0]
        errors.append(float(y[j]-X[j]@beta))
    err=np.array(errors)
    return {"rmse":float(np.sqrt(np.mean(err*err))),
            "squared_errors":(err*err).tolist()}

def audit(source:Path):
    import numpy as np
    m=upstream()
    original=m.check_source(Path(source))
    survey,captures=m.source_frame(original)
    outcomes=m.site_outcomes(original)
    garden_rows=m.assembled(survey,captures,outcomes)[0]
    by={(r["garden"],r["species"]):r for r in garden_rows}
    coords={int(r["Id"]):(float(r["latitude"]),float(r["longitude"]))
            for r in m.csv_source(original,"03_site_data/garden_site_coordinates.csv")}
    if len(garden_rows)!=96 or len(coords)!=24 or len(by)!=96:
        raise ValueError("Expected 24 by four independent garden/species rows")
    flowers={}
    for (g,date,time),event in survey.items():
        for species in ("Carrot","Radish"):
            n=event["flowers"][species]
            if n is None:continue
            record=flowers.setdefault((g,species),[0.,0.,0.])
            record[0]+=n*event["hours"]
            record[1]+=event["hours"]
            record[2]+=(1. if n>0 else 0.)*event["hours"]
    gardens=sorted(coords)
    if any(flowers[g,sp][1]<=0 for g in gardens for sp in ("Carrot","Radish")):
        raise ValueError("Missing flower availability exposure")
    geo=np.array([coords[g] for g in gardens])
    geo-=geo.mean(axis=0)
    all_results={}
    for species in ("Carrot","Radish"):
        y=np.array([by[g,species]["response"] for g in gardens])
        rates=np.array([by[g,species]["rate"] for g in gardens])
        base=np.column_stack([np.ones(len(gardens)),np.log1p(rates)])
        results={}
        for control in ("none","mean_flowers","positive_flower_window_share","latitude_longitude"):
            if control=="none": X=base
            elif control=="mean_flowers":
                X=np.column_stack([base,np.log1p([flowers[g,species][0]/flowers[g,species][1] for g in gardens])])
            elif control=="positive_flower_window_share":
                X=np.column_stack([base,[flowers[g,species][2]/flowers[g,species][1] for g in gardens]])
            else:
                X=np.column_stack([base,geo])
            baseline=independent_loo(y,X)
            variants={}
            other="Carrot" if species=="Radish" else "Radish"
            for kind,donor in (("own",species),("crossplant",other)):
                xs=[]
                for g in gardens:
                    row=by[g,donor]
                    total=row["n_visits"]
                    if total<=0:raise ValueError("Undefined donor visit proportions")
                    xs.append([row["counts"]["apis"]/total,row["counts"]["other_nonbee"]/total])
                fit=independent_loo(y,np.column_stack([X,np.array(xs)]))
                fit["rmse_change_pct_relative_to_total"]=100*(1-fit["rmse"]/baseline["rmse"])
                fit["donor_plant"]=donor
                fit["gardens_with_lower_squared_error"]=sum(a<b for a,b in zip(fit["squared_errors"],baseline["squared_errors"]))
                variants[kind]=fit
            results[control]={"baseline":baseline,**variants}
        all_results[species]=results
    return {
        "schema":"BALANCE_ZURICH_CROSSPLANT_DIAGNOSTIC_V1",
        "garden_count":len(gardens),
        "species_examined":["Carrot","Radish"],
        "shared_same_garden_context":True,
        "crossplant_exposure_is_a_negative_control":False,
        "plant_specific_causation_identified":False,
        "V4_inputs_modified":False,
        "original_source_sha256":m.SOURCE_SHA256,
        "results":all_results,
        "interpretation_ceiling":"Borrowed composition may index shared garden conditions or shared insect communities; no randomized exposure, causal pollinator effect or matched BALANCE worldline."
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    args=p.parse_args()
    result=audit(args.source)
    args.out_dir.mkdir(parents=True,exist_ok=False)
    (args.out_dir/"CROSSPLANT_RESULTS.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    with (args.out_dir/"CROSSPLANT_CV.csv").open("w",newline="") as f:
        wr=csv.writer(f)
        wr.writerow(["response","control","comparison","rmse","delta_pct","n_better","donor"])
        for species,groups in result["results"].items():
            for control,items in groups.items():
                wr.writerow([species,control,"total_only",items["baseline"]["rmse"],0,"",""])
                for k in ("own","crossplant"):
                    row=items[k]
                    wr.writerow([species,control,k,row["rmse"],row["rmse_change_pct_relative_to_total"],row["gardens_with_lower_squared_error"],row["donor_plant"]])
    print(json.dumps({s:{c:{k:round(v[k]["rmse_change_pct_relative_to_total"],2) for k in ("own","crossplant")} for c,v in g.items()} for s,g in result["results"].items()},indent=2))
