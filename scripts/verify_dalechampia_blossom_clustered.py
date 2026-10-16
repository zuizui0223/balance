#!/usr/bin/env python3
"""Independently verify authentic-source blossom/maternal sensitivity readout.

This compares outputs of a posthoc sensitivity estimator, not the 2015 paper's
maternal random-intercept nlme specification or any carbon pathway.
"""
from __future__ import annotations

import argparse
import json
from math import isclose
from pathlib import Path


def verify(frozen: dict, observed: dict) -> dict:
    if frozen.get("schema_version") != "DALECHAMPIA_2015_BLOSSOM_CLUSTERED_FROZEN_V1":
        raise ValueError("source sensitivity freeze version mismatch")
    if observed.get("schema_version") != "DALECHAMPIA_2015_BLOSSOM_CLUSTERED_SENSITIVITY_V1":
        raise ValueError("observed blossom source result version mismatch")
    if observed.get("source_file_sha256") != frozen["original_source_file_sha256"]:
        raise ValueError("original biological data SHA256 does not match freeze")
    if observed.get("status") != "ORIGINAL_DRYAD_OBSERVATIONAL_CLUSTER_SENSITIVITY_NOT_PUBLISHED_MODEL":
        raise ValueError("source result has wrong nonconfirmatory claim status")
    if any(observed.get(k) is not v for k,v in (
        ("published_seed_mass_mixed_model_reproduced",False),
        ("direct_structural_BALANCE_identified",False),
        ("registered_abortion_proxy_is_numeric_not_morphological",True),
        ("pooled_different_studies",False),
    )):
        raise ValueError("experimental source overpromoted or relabelled")
    actual_models=observed.get("analyses")
    frozen_models=frozen.get("models")
    if not isinstance(actual_models,dict) or set(actual_models)!=set(frozen_models):
        raise ValueError("source analysis lane set changed")
    keys=("n_seed_rows","n_blossoms","n_maternal_plants","with_seedset_covariate")
    for lane, ref in frozen_models.items():
        model=actual_models[lane]
        if any(model.get(k)!=ref[k] for k in keys):
            raise ValueError(f"{lane} original source-unit support changed")
        if set(model.get("effects",{})) != set(ref["effects"]):
            raise ValueError(f"{lane} registered treatment arms changed")
        for arm, expected in ref["effects"].items():
            observed_arm=model["effects"][arm]
            if observed_arm.get("witnesses_zero_in_interval") is not expected["witnesses_zero_in_interval"]:
                raise ValueError(f"{lane} {arm} interval sign classification drifted")
            for field in ("mean_difference_mg","maternal_cluster_robust_se_mg"):
                if not isclose(observed_arm.get(field,float("nan")),expected[field],
                               rel_tol=0,abs_tol=0.00005):
                    raise ValueError(f"{lane} {arm} source coefficient or uncertainty drift")
            out=observed_arm.get("asymptotic_wald_95_interval_mg")
            if (not isinstance(out,list) or len(out)!=2 or
                    any(not isclose(a,b,rel_tol=0,abs_tol=.00005)
                        for a,b in zip(out,expected["asymptotic_wald_95_interval_mg"]))):
                raise ValueError(f"{lane} {arm} source 95% interval drift")
    assert frozen["inference_limits"]["source_published_mixed_model_reproduced"] is False
    assert frozen["inference_limits"]["structural_balance_occupancy_identified"] is False
    return {
        "status":"AUTHENTIC_DALECHAMPIA_BLOSSOM_CLUSTERED_SENSITIVITY_REPLAYED",
        "verified_model_lanes":len(actual_models),
        "verified_treatment_contrasts":sum(len(x["effects"]) for x in actual_models.values()),
        "original_2015_published_nlme_reproduced":False,
        "structural_BALANCE_identified":False,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--frozen",type=Path,required=True)
    parser.add_argument("--computed",type=Path,required=True)
    args=parser.parse_args()
    f=json.loads(args.frozen.read_text(encoding="utf-8"))
    d=json.loads(args.computed.read_text(encoding="utf-8"))
    print(json.dumps(verify(f,d),sort_keys=True))


if __name__=="__main__":
    main()
