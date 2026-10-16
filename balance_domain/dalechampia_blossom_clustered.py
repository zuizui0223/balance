"""Exact-source, blossom-level clustered sensitivity for Pélabon et al. 2015.

This is a retrospective independent statistical analysis, NOT reproduction of
the published nlme maternal-random-intercept model. Seed measurements are
nested in manipulated blossoms, which are nested in mothers. The fixed-effect
analysis collapses seeds within each blossom *before* estimating treatment
contrasts, controls for mother identity and peduncle diameter, and reports
maternal-cluster-robust asymptotic Wald intervals.

The bag manipulation obscured the ENTIRE blossom (including fruits), not only
the bracts. The numeric >=20 mg exclusion has the same counts as the paper's
morphologically diagnosed abortions, but is not proof of that diagnosis.
No carbon-pathway, structural architecture, or BALANCE effect is identified.
"""
from __future__ import annotations

import hashlib
import io
import math

from .dalechampia_method_scope import (
    FILE_IDENTITIES,
    verify_exact_dryad_bytes,
)

SCHEMA = "DALECHAMPIA_2015_BLOSSOM_CLUSTERED_SENSITIVITY_V1"
ARMS = ("bag", "cut", "cutcont")
EXPECTED = {
    "all_nonmissing": {"seeds": 1220, "blossoms": 142, "mothers": 37},
    "numeric_ge20_proxy": {"seeds": 1103, "blossoms": 132, "mothers": 36},
}


def fit_blossom_clustered(df, *, with_seedset: bool = False) -> dict:
    """Fit one observation per blossom, mother FE + mother-clustered covariance.

    Expects a pandas dataframe with *one row per original measured seed*.
    This function is also testable on synthetic samples; only the wrapper
    analyze_authenticated_blossom_clusters() licenses original-source use.
    """
    import pandas as pd
    import statsmodels.formula.api as smf

    if not isinstance(df, pd.DataFrame):
        raise ValueError("seed records must be a pandas DataFrame")
    required = {"FemaleID", "crossID", "treatcode", "seedmass", "ped", "seedset"}
    if not required.issubset(df.columns):
        raise ValueError("seed records lack original experimental identity fields")
    if df.empty or df[list(required)].isna().any().any():
        raise ValueError("input must contain complete selected seed measurements and identities")
    if not set(df["treatcode"]).issubset({"bag", "cut", "cutcont", "cont"}):
        raise ValueError("seed treatments not among four original arms")
    df = df.copy()
    df["FemaleID"] = df["FemaleID"].astype(str)
    df["crossID"] = df["crossID"].astype(str)

    # One (mother, blossom) must have a single experimental assignment,
    # single peduncle diameter and single observed seed set.
    structure = df.groupby(["FemaleID", "crossID"], observed=True).agg(
        arm_n=("treatcode", "nunique"),
        ped_n=("ped", "nunique"),
        seedset_n=("seedset", "nunique"),
    )
    if (structure[["arm_n", "ped_n", "seedset_n"]] > 1).any().any():
        raise ValueError("within-blossom treatment or design covariate inconsistency")
    if not df["seedmass"].map(math.isfinite).all() or (df["seedmass"] < 0).any():
        raise ValueError("original seed mass must be finite and non-negative")

    blossoms = (df.groupby(["FemaleID", "crossID", "treatcode"],
                           as_index=False, observed=True)
                .agg(seedmass=("seedmass", "mean"),
                     ped=("ped", "first"),
                     seedset=("seedset", "first"),
                     seed_n=("seedmass", "size")))
    if (blossoms["seed_n"] <= 0).any():
        raise ValueError("empty blossom mean is not admissible")
    blossoms["treatcode"] = pd.Categorical(
        blossoms["treatcode"], categories=["cont", "bag", "cut", "cutcont"]
    )
    if len(blossoms) <= blossoms["FemaleID"].nunique() + 5:
        raise ValueError("insufficient independent blossom assignments for maternal fixed effects")
    for arm in ["cont", *ARMS]:
        if not (blossoms["treatcode"] == arm).any():
            raise ValueError(f"registered treatment {arm} not represented")
    formula = ('seedmass ~ ped + C(treatcode, Treatment(reference="cont"))'
               + (" + seedset" if with_seedset else "")
               + " + C(FemaleID)")
    fit = smf.ols(formula, data=blossoms).fit(
        cov_type="cluster",
        cov_kwds={"groups": blossoms["FemaleID"], "use_correction": True,
                  "df_correction": True},
        use_t=False,
    )
    effects = {}
    for arm in ARMS:
        term = f'C(treatcode, Treatment(reference="cont"))[T.{arm}]'
        ci = fit.conf_int(alpha=0.05).loc[term].tolist()
        out = [float(fit.params[term]), float(fit.bse[term]), *ci]
        if not all(map(math.isfinite, out)):
            raise ValueError("cluster-robust source estimate not finite")
        effects[f"{arm}_minus_cont"] = {
            "mean_difference_mg": round(out[0], 6),
            "maternal_cluster_robust_se_mg": round(out[1], 6),
            "asymptotic_wald_95_interval_mg": [round(out[2], 6), round(out[3], 6)],
            "witnesses_zero_in_interval": out[2] <= 0 <= out[3],
        }
    return {
        "n_seed_rows": len(df),
        "n_blossoms": len(blossoms),
        "n_maternal_plants": blossoms["FemaleID"].nunique(),
        "n_seed_rows_per_blossom_min": int(blossoms["seed_n"].min()),
        "with_seedset_covariate": with_seedset,
        "formula_semantics": (
            "one_observation_per_blossom + peduncle + maternal_fixed_effects"
            + (" + seedset" if with_seedset else "")
        ),
        "interval_method": "clustered_maternal_robust_normal_Wald_95_with_finite_cluster_covariance_correction",
        "original_2015_mixed_model_reproduced": False,
        "original_random_intercept_nlme_AIC_reproduced": False,
        "effects": effects,
    }


def analyze_authenticated_blossom_clusters(contract: dict,
                                          files: dict[str, bytes]) -> dict:
    """Reject files until both ORIGINAL archival MD5/size checks succeed."""
    import pandas as pd

    source = verify_exact_dryad_bytes(contract, files)
    if source["status"] != "EXACT_DRYAD_BYTES_VERIFIED_SUPPORT_ONLY_NO_MODELS":
        raise ValueError("original Dryad authentication and source-unit gate failed")
    if source["raw_seed_records"] != 1221 or source["raw_seed_missing_mass"] != 1:
        raise ValueError("original source seed support drift")
    if not source["recorded_mass_counts_match_published_seeds"]:
        raise ValueError("source arm support is inconsistent with publication")
    if not source["numeric_below_20_counts_match_published_abortions"]:
        raise ValueError("numeric threshold source audit differs from reported count")

    source_name = FILE_IDENTITIES[46163][0]
    data = pd.read_csv(
        io.BytesIO(files[source_name]), sep="\t", encoding="latin-1",
        decimal=",", dtype={"FemaleID": "str", "crossID": "str"},
    )
    if len(data) != 1221 or int(data["seedmass"].isna().sum()) != 1:
        raise ValueError("raw file read changed seed count/missingness")
    if int(data["seedmass"].lt(20).sum()) != 117:
        raise ValueError("20-mg mass proxy count changed")

    analyses = {}
    for lane, selected in (
        ("all_nonmissing", data.loc[data["seedmass"].notna()].copy()),
        ("numeric_ge20_proxy", data.loc[data["seedmass"] >= 20].copy()),
    ):
        for adjust_seedset in (False, True):
            name = f"{lane}__{'plus_seedset' if adjust_seedset else 'ped_only'}"
            result = fit_blossom_clustered(selected, with_seedset=adjust_seedset)
            wanted = EXPECTED[lane]
            if ((result["n_seed_rows"], result["n_blossoms"], result["n_maternal_plants"])
                    != (wanted["seeds"], wanted["blossoms"], wanted["mothers"])):
                raise ValueError(f"{lane} original-source unit or eligibility drift")
            analyses[name] = result
    return {
        "schema_version": SCHEMA,
        "status": "ORIGINAL_DRYAD_OBSERVATIONAL_CLUSTER_SENSITIVITY_NOT_PUBLISHED_MODEL",
        "source_dataset_doi": "10.5061/dryad.nb675",
        "source_file_sha256": {
            name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(files.items())
        },
        "seed_mass_units": "mg_per_seed_as_blossom_mean",
        "source_level": "original_public_raw_seed_data",
        "intervention_unit": "hand_pollinated_blossom",
        "independent_uncertainty_cluster": "maternal_plant",
        "pooled_different_studies": False,
        "registered_abortion_proxy_is_numeric_not_morphological": True,
        "causal_estimate_specific_to_bract_photosynthesis": False,
        "published_seed_mass_mixed_model_reproduced": False,
        "direct_structural_BALANCE_identified": False,
        "added_independent_biological_clusters": 0,
        "analyses": analyses,
        "claim_ceiling": (
            "posthoc source-authenticated maternal-FE blossom-unit robust sensitivity; "
            "not published nlme specification, carbon-transfer mechanism, lifetime "
            "fitness or structural architecture comparison"
        ),
    }
