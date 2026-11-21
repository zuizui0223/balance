"""Published bee-learning audit and provenance-checked paired CSV diagnostics.

The reported statistics are transcribed from the paper. Descriptive contrasts
computed from a local CSV carry a separate indication of whether the supplied
bytes match the archived Dryad file. Trial is repeated within BeeID, nested
in ColonyID; no flower-level or visit-level pseudo-replication is allowed.

The original sequence was always NAIVE then EXPERIENCED ~24 hours later, so
paired descriptive differences are not randomized learning causality.
"""
from __future__ import annotations

from collections import defaultdict
import csv
from hashlib import sha256
from io import StringIO
import json
from math import isfinite, log1p
from pathlib import Path
from statistics import mean

SOURCE = (
    Path(__file__).resolve().parents[1] /
    "data/BALANCE_BEE_LEARNING_DUAL_FUNCTION_2024_SOURCE_V1.json"
)
STUDY_DOI = "10.1093/beheco/arae083"
DATA_DOI = "10.5061/dryad.gtht76hwk"
# Archive metadata published at https://datadryad.org/api/v2/files/3536167.
DRYAD_IDENTITY = {
    "primary_file_id": 3536167,
    "primary_version_id": 321573,
    "primary_file": "AnalysisData_All-Trials-Summary-Data_20_8-4-2024.csv",
    "primary_file_size_bytes": 27774,
    "primary_file_sha256": "4abb4300cfe5202058dd51003c5910e65c8c6cb774cd8b8100e8d5563b1433cb",
}
REQUIRED_CLAIM_CEILINGS = {
    "species_specific_percent_changes_are_point_estimates",
    "overall_stigma_nonsignificance_does_not_establish_equivalence",
    "species_by_experience_interaction_is_a_real_published_positive_statistical_result",
    "not_a_randomized_learning_vs_aging_sequence",
    "same_bee_repeated_trials_and_colony_clustering_required",
    "no_genetically_assigned_donor_paternity",
    "stigma_deposition_proxy_not_measured_female_seed_fitness",
    "pollen_basket_collection_not_equivalent_to_complete_pollen_loss",
    "same_species_S_elaeagnifolium_in_2022_anther_joining_study",
    "cross_paper_mediation_in_same_taxon_not_identified",
    "not_independent_four_evolutionary_origins",
    "U2_U6_V4_admissions_unchanged",
    "title_words_do_not_substitute_for_reported_interaction",
    "no_new_effect_or_p_value_estimated",
}
MISSING_IDS = {"", "na", "n/a", "nan", "null", "none"}
ESSENTIAL_COLUMNS = (
    "BeeID", "ColonyID", "Species", "Treatment", "NumVisits",
    "CorbPolperVis", "StigPolperVis",
)


def validate_publication_receipt(path: Path = SOURCE) -> dict:
    source = json.loads(path.read_text(encoding="utf-8"))
    if (
        source.get("schema_version")
        != "BALANCE_BEE_LEARNING_DUAL_FUNCTION_PUBLICATION_AUDIT_V1"
        or source.get("status")
        != "ORIGINAL_PUBLISHED_EFFECTS_AND_DRYAD_SCHEMA_ONLY_NOT_RAW_REFIT"
        or source["article"]["doi"] != STUDY_DOI
        or source["archived_data"]["doi"] != DATA_DOI
    ):
        raise ValueError("Published paper or Dryad evidence contract changed")
    exp = source["experiment"]
    if exp["replicate_unit"] != "BEEID_WITHIN_COLONYID":
        raise ValueError("Bee/colony dependence may not be collapsed to flowers")
    if exp["colonies_per_species_at_least"] < 3:
        raise ValueError("Original multi-colony design source changed")
    if not exp["same_bee_24h_order_confounded"]:
        raise ValueError("Fixed temporal sequence may not be called randomized")
    species = exp["plant_species"]
    if len(species) != 4 or len({x["code"] for x in species}) != 4:
        raise ValueError("Expected four different original flower species")
    expected = {
        "PHCA": ("Phacelia campanularia", 17, 18, 1.876),
        "EXAF": ("Exacum affine", 19, 28, 2.126),
        "SOEL": ("Solanum elaeagnifolium", 26, -49, 2.276),
        "MIGU": ("Erythranthe guttata", 27, -6, 2.925),
    }
    for x in species:
        name, collection_pct, stigma_pct, complexity = expected.get(
            x["code"], (None, None, None, None)
        )
        if (
            x["species"] != name
            or x["pollen_collection_percent_experienced_vs_naive"]
            != collection_pct
            or x["stigma_deposition_percent_experienced_vs_naive"]
            != stigma_pct
            or x["floral_complexity_mfci"] != complexity
        ):
            raise ValueError("Published species-specific original results altered")
    p = source["published_results"]
    if (
        p["collection_experience"]["overall_change_percent"] != 22
        or p["collection_experience"]["per_time_change_percent"] != 24
        or p["collection_experience"]["p"] != 0.0017
        or p["collection_experience"]["species_by_experience_p"] != 0.961
        or p["stigmatic_deposition_experience"]["overall_p"] != 0.893
        or p["stigmatic_deposition_experience"]["species_by_experience_p"] != 0.004
        or p["modified_motor_routine"][
            "stigmatic_deposition_species_experience_routine_p"
        ] != 0.00005
    ):
        raise ValueError("Original paper global/interaction results changed")
    archive = source["archived_data"]
    if any(archive.get(key) != expected for key, expected in DRYAD_IDENTITY.items()):
        raise ValueError("Dryad file identity differs from the published archive metadata")
    if (
        archive.get("raw_csv_retrieved") is not False
        or archive.get("original_trial_data_refitted") is not False
    ):
        raise ValueError("Publication-only source archive cannot claim raw retrieval or refit")
    ceiling = source.get("source_claim_ceiling")
    if (
        not isinstance(ceiling, dict)
        or not REQUIRED_CLAIM_CEILINGS.issubset(ceiling)
        or any(value is not True for value in ceiling.values())
    ):
        raise ValueError("This source cannot be promoted to fitness or V4 evidence")
    return source


def published_dual_function_audit(path: Path = SOURCE) -> dict:
    """Reconcile non-significant global stigma with real species interaction."""
    src = validate_publication_receipt(path)
    p = src["published_results"]
    species = src["experiment"]["plant_species"]
    effects = [
        {
            "species": s["species"],
            "dryad_species_code": s["code"],
            "floral_complexity_mfci": s["floral_complexity_mfci"],
            "published_collection_percent_change": s[
                "pollen_collection_percent_experienced_vs_naive"
            ],
            "published_stigma_percent_change": s[
                "stigma_deposition_percent_experienced_vs_naive"
            ],
            "published_stigma_species_contrast": "REPORTED_NONSIGNIFICANT",
            "published_collection_species_contrast": "NOT_REPORTED",
        }
        for s in species
    ]
    return {
        "analysis": "BALANCE_BEE_LEARNING_BASKET_VS_STIGMA_SOURCE_V1",
        "status": "PUBLISHED_SOURCE_ONLY_NOT_ORIGINAL_RAW_DATA_REFIT",
        "doi": STUDY_DOI,
        "dryad_doi": DATA_DOI,
        "original_independent_research_programmes": 1,
        "flower_species": len(effects),
        "collection_positive_percent_all_species": sum(
            x["published_collection_percent_change"] > 0 for x in effects
        ),
        "stigma_direction_positive_species": sum(
            x["published_stigma_percent_change"] > 0 for x in effects
        ),
        "stigma_direction_negative_species": sum(
            x["published_stigma_percent_change"] < 0 for x in effects
        ),
        "published_global_collection_change_percent": p[
            "collection_experience"]["overall_change_percent"
        ],
        "published_global_collection_p": p["collection_experience"]["p"],
        "published_global_stigma_p": p[
            "stigmatic_deposition_experience"]["overall_p"
        ],
        "published_species_by_experience_stigma_interaction_p": p[
            "stigmatic_deposition_experience"]["species_by_experience_p"
        ],
        "published_species_by_experience_collection_interaction_p": p[
            "collection_experience"]["species_by_experience_p"
        ],
        "published_routine_by_species_by_experience_stigma_p": p[
            "modified_motor_routine"
        ]["stigmatic_deposition_species_experience_routine_p"],
        "published_stigma_experience_term_scope": p[
            "stigmatic_deposition_experience"
        ]["experience_term_scope"],
        "published_source_statistic_discrepancy": p[
            "modified_motor_routine"
        ]["stigmatic_deposition_main_discrepancy"],
        "species_source_point_estimates": effects,
        "within_bee_24h_experience_order_not_randomized": True,
        "stigma_pollination_not_seed_fitness": True,
        "shared_S_elaeagnifolium_with_Solanum_2022_not_evolutionary_replicate": True,
        "new_published_effects_fitted_by_this_audit": 0,
        "source_data_rows_accessed": 0,
        "claim_ceiling": (
            "published_collection_gain_and_species_heterogeneous_stigma_"
            "deposition_not_proof_of_equal_pollination_or_plant_fitness"
        ),
    }


def _nonnegative_number(value: str, *, field: str, line: int) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"line {line} invalid {field}") from exc
    if not isfinite(parsed) or parsed < 0:
        raise ValueError(f"line {line} invalid {field}")
    return parsed


def load_original_paired_csv(csv_path: Path) -> dict:
    """Compute paired diagnostics and identify the supplied bytes against Dryad."""
    if not csv_path.is_file():
        raise FileNotFoundError(
            "Original Dryad CSV not locally supplied; cannot run raw paired analysis"
        )
    # Hash and parse one snapshot, even if the path is replaced during the audit.
    contents = csv_path.read_bytes()
    digest = sha256(contents).hexdigest()
    verified = (
        digest == DRYAD_IDENTITY["primary_file_sha256"]
        and len(contents) == DRYAD_IDENTITY["primary_file_size_bytes"]
    )
    with StringIO(contents.decode("utf-8-sig"), newline="") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []
        if len(header) != len(set(header)) or not set(ESSENTIAL_COLUMNS) <= set(header):
            raise ValueError("CSV is missing canonical bee/colony/two-function columns")
        data = list(reader)
    if not data or any(None in row or None in row.values() for row in data):
        raise ValueError("Empty or ragged CSV")
    allowed_species = {"PHCA", "EXAF", "SOEL", "MIGU"}
    bee_groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for line, row in enumerate(data, start=2):
        bee = row["BeeID"].strip()
        colony = row["ColonyID"].strip()
        species = row["Species"].strip().upper()
        # The public README gives Erythranthe guttata as ERGU/MIGU;
        # normalize only that exact documented synonym, not an arbitrary taxon.
        if species == "ERGU":
            species = "MIGU"
        treatment = row["Treatment"].strip().casefold().replace("ï", "i")
        if (
            bee.casefold() in MISSING_IDS
            or colony.casefold() in MISSING_IDS
            or species not in allowed_species
        ):
            raise ValueError(f"line {line} unidentifiable bee/colony/species")
        if treatment not in {"naive", "experienced"}:
            raise ValueError(f"line {line} invalid or missing experience treatment")
        n = _nonnegative_number(row["NumVisits"], field="NumVisits", line=line)
        if not 1 <= n <= 70 or not n.is_integer():
            raise ValueError(f"line {line} invalid number of flower visits")
        basket = _nonnegative_number(
            row["CorbPolperVis"], field="CorbPolperVis", line=line
        )
        stigma = _nonnegative_number(
            row["StigPolperVis"], field="StigPolperVis", line=line
        )
        bee_groups[(colony, bee)].append({
            "species": species, "treatment": treatment,
            "visits": int(n), "basket": basket, "stigma": stigma,
        })
    pairs = []
    missing_treatments = []
    n_colonies_by_species: dict[str, set[str]] = defaultdict(set)
    for (colony, bee), records in sorted(bee_groups.items()):
        species = {x["species"] for x in records}
        if len(species) != 1:
            raise ValueError("Same bee reused across species; incompatible paired grain")
        s = next(iter(species))
        n_colonies_by_species[s].add(colony)
        treatments = [x["treatment"] for x in records]
        if len(treatments) != len(set(treatments)):
            raise ValueError("Duplicate bee trial/treatment rows; no fake replication")
        if set(treatments) != {"naive", "experienced"}:
            missing_treatments.append({"bee": bee, "colony": colony, "species": s})
            continue
        a = next(x for x in records if x["treatment"] == "naive")
        b = next(x for x in records if x["treatment"] == "experienced")
        if a["visits"] != b["visits"]:
            raise ValueError("Paired source experiment requires matched visit counts")
        pairs.append({
            "species": s, "colony": colony, "bee": bee,
            "delta_log1p_basket_per_visit": log1p(b["basket"])-log1p(a["basket"]),
            "delta_log1p_stigma_per_visit": log1p(b["stigma"])-log1p(a["stigma"]),
            "visits_in_each_trial": a["visits"],
        })
    if not pairs:
        raise ValueError("No valid matched bee trials in supplied CSV")
    by_species: dict[str, list[dict]] = defaultdict(list)
    for p in pairs:
        by_species[p["species"]].append(p)
    return {
        "status": (
            "VERIFIED_DRYAD_CSV_PAIRED_DESCRIPTIVES" if verified
            else "UNVERIFIED_USER_CSV_PAIRED_DESCRIPTIVES"
        ),
        "provenance": {
            "verified_original": verified,
            "observed_sha256": digest,
            "observed_size_bytes": len(contents),
            "expected_sha256": DRYAD_IDENTITY["primary_file_sha256"],
            "expected_size_bytes": DRYAD_IDENTITY["primary_file_size_bytes"],
            "expected_filename": DRYAD_IDENTITY["primary_file"],
            "file_id": DRYAD_IDENTITY["primary_file_id"],
            "version_id": DRYAD_IDENTITY["primary_version_id"],
            "doi": DATA_DOI,
        },
        "paired_bee_trial_count": len(pairs),
        "unpaired_bee_count": len(missing_treatments),
        "unpaired_bees_excluded_from_paired_summary": True,
        "species_results": [
            {
                "species_code": s,
                "n_paired_bees": len(group),
                "n_colonies_of_paired_bees": len({x["colony"] for x in group}),
                "mean_within_bee_delta_log1p_pollen_basket_per_visit": mean(
                    x["delta_log1p_basket_per_visit"] for x in group
                ),
                "mean_within_bee_delta_log1p_stigma_pollen_per_visit": mean(
                    x["delta_log1p_stigma_per_visit"] for x in group
                ),
                "not_independent_per_flower_samples": True,
            }
            for s, group in sorted(by_species.items())
        ],
        "colonies_observed_in_supplied_csv_by_species": {
            s: len(groups) for s, groups in sorted(n_colonies_by_species.items())
        },
        "no_new_p_values_or_causal_paternity": True,
        "no_claim_that_before_after_order_was_randomized": True,
        "no_claim_that_flower_species_are_independent_phylogenetic_origins": True,
        "note": (
            "Within-bee per-visit count changes are descriptive log1p contrasts, "
            "not the original authors' GLMM and not direct plant fitness. "
            "Check colony effects, order and zero inflation before inference."
        ),
    }
