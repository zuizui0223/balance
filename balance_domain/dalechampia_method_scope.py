"""Source-locked Dalechampia 2015 treatment-scope and Dryad recovery audit.

This is an evidence-integrity layer, not a new carbon-transport estimate,
a structural architecture worldline or a mixed-effects model reproduction.

Original experimental labels:
    cont    = hand-pollinated, undisturbed after pollination
    cut     = both bracts removed
    cutcont = both bracts marginally trimmed as a cutting control
    bag     = ENTIRE pollinated blossom enclosed in perforated aluminium foil

Consequently "bag" is NOT bract-only photosynthesis suppression. Its
seed-mass contrast cannot isolate carbon fixed by bracts from fruit
photosynthesis, microclimate, light environment, or manipulation effects.
"""
from __future__ import annotations

import csv
import hashlib
import io
import math
import re
from collections import Counter, defaultdict

SCHEMA = "DALECHAMPIA_POSTANTHESIS_METHOD_AND_DRYAD_V2"
ARMS = ("bag", "cut", "cutcont", "cont")
FILE_IDENTITIES = {
    46163: ("Pelabon et al FE file 1.txt", 84562,
            "0d64b8a35835bfd23e0feab9276026bb"),
    46164: ("Pelabon et al FE file 2.txt", 4821,
            "4b06aa5894f0c3ff361ee225a1f81ee5"),
}
SOURCE_SEED_COUNTS = {"bag": 317, "cut": 295, "cutcont": 317, "cont": 291}
SOURCE_ABORTED_COUNTS = {"bag": 33, "cut": 25, "cutcont": 39, "cont": 20}


def _text(v, name):
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"{name} must be nonblank source text")
    return v.strip()


def _require_false(value, name):
    if value is not False:
        raise ValueError(f"{name} must remain false until separately identified")


def audit_dalechampia_method_scope(c: dict) -> dict:
    """Audit historical experimental assignment, not the efficacy of channels."""
    if not isinstance(c, dict) or set(c) != {
        "schema_version", "status", "article_doi", "article_methods_url",
        "dryad_doi", "dryad_dataset_url", "dryad_version_id",
        "source_methods", "original_arms", "source_totals",
        "dryad_source_files", "source_access", "identification", "next_stage"
    }:
        raise ValueError("Dalechampia V2 source contract schema changed")
    if c["schema_version"] != SCHEMA:
        raise ValueError("Dalechampia V2 source schema mismatch")
    if c["status"] != "ORIGINAL_METHOD_SOURCE_VERIFIED_RAW_BYTES_NOT_ACQUIRED":
        raise ValueError("published source methods are not labelled as unexecuted raw")
    if c["article_doi"] != "10.1111/1365-2435.12427" or c["dryad_doi"] != "10.5061/dryad.nb675":
        raise ValueError("Dalechampia source DOI mismatch")
    if c["dryad_version_id"] != 11209:
        raise ValueError("Dryad version ID mismatch")
    if not str(c["article_methods_url"]).startswith("https://"):
        raise ValueError("source methods URL must be HTTPS")
    if not str(c["dryad_dataset_url"]).startswith("https://"):
        raise ValueError("Dryad dataset URL must be HTTPS")

    methods = c["source_methods"]
    if (methods["year"], methods["n_maternal_plants"],
            methods["n_maternal_plants_with_four_treatments_completed"]) != (2013, 39, 33):
        raise ValueError("original greenhouse sample sizes/date changed")
    if methods["all_treatments_male_inflorescence_removed_in_female_phase"] is not True:
        raise ValueError("all treatments used post-hand-pollination male inflorescence removal")
    if methods["raw_seed_mass_analysis_requires_maternal_plant_clustering"] is not True:
        raise ValueError("seeds and blossoms within maternal plants are dependent")
    if methods["abortion_morphology_not_identified_from_numeric_mass_alone"] is not True:
        raise ValueError("aborted-seed status cannot be inferred from seed mass alone")
    _text(methods["outcome"], "outcome")
    arms = c["original_arms"]
    if not isinstance(arms, list) or len(arms) != 4:
        raise ValueError("four historical source treatment arms required")
    observed = {}
    for item in arms:
        if not isinstance(item, dict) or set(item) != {
            "code", "description", "bracts_retained", "foil_entire_blossom",
            "bracts_physically_cut", "selective_bract_photosynthesis_disabled",
        }:
            raise ValueError("historical treatment scope keys changed")
        code = _text(item["code"], "code")
        if code in observed or code not in ARMS:
            raise ValueError("duplicate/unknown historical treatment code")
        _text(item["description"], "arm description")
        observed[code] = item
        if type(item["selective_bract_photosynthesis_disabled"]) is not bool:
            raise ValueError("selective_bract_photosynthesis_disabled must be boolean")
        _require_false(item["selective_bract_photosynthesis_disabled"],
                       "published bract-only light intervention")
    if set(observed) != set(ARMS):
        raise ValueError("incomplete historical treatment arms")
    expected_flags = {
        "bag": (True, True, False),
        "cut": (False, False, True),
        "cutcont": (True, False, True),
        "cont": (True, False, False),
    }
    for name, flags in expected_flags.items():
        recorded = tuple(observed[name][key] for key in (
            "bracts_retained", "foil_entire_blossom", "bracts_physically_cut"))
        if recorded != flags:
            raise ValueError(f"{name} source intervention targets changed")
    if "ENTIRE" not in observed["bag"]["description"]:
        raise ValueError("foil covered ENTIRE pollinated blossom, not only bracts")
    if "approximately 1 mm" not in observed["cutcont"]["description"]:
        raise ValueError("cut-control was marginal bract trim not complete removal")
    totals = c["source_totals"]
    if totals["seed_count"] != SOURCE_SEED_COUNTS:
        raise ValueError("source reported seed counts changed")
    if totals["reported_aborted_seed_count"] != SOURCE_ABORTED_COUNTS:
        raise ValueError("source reported aborted counts changed")
    if totals["aborted_seed_morphology_separately_observed_by_authors"] is not True:
        raise ValueError("original abortion assignment included morphology")
    _require_false(totals["abort_identification_by_mass_threshold_alone_valid"],
                   "numeric abortion proxy")

    files = c["dryad_source_files"]
    if not isinstance(files, list) or len(files) != 2:
        raise ValueError("two independent Dryad text file identities required")
    file_map = {}
    for f in files:
        file_id = f["source_file_id"]
        if type(file_id) is not int or file_id not in FILE_IDENTITIES or file_id in file_map:
            raise ValueError("unknown/duplicate Dryad file ID")
        filename, size, digest = FILE_IDENTITIES[file_id]
        if (f["name"], f["size_bytes"], f["md5"]) != (filename, size, digest):
            raise ValueError("Dryad original name/size/MD5 identity drift")
        if f["api_metadata_url"] != f"https://datadryad.org/api/v2/files/{file_id}":
            raise ValueError("Dryad metadata provenance changed")
        if f["download_url"] != f"https://datadryad.org/api/v2/files/{file_id}/download":
            raise ValueError("Dryad file download provenance changed")
        if not isinstance(f["expected_fields"], list) or not f["expected_fields"]:
            raise ValueError("Dryad documented fields are required")
        file_map[file_id] = f
    if set(file_map) != set(FILE_IDENTITIES):
        raise ValueError("missing Dryad file identity")

    source = c["source_access"]
    if source["original_article_verified"] is not True or source["dryad_metadata_verified"] is not True:
        raise ValueError("original methods and dataset metadata must be verified")
    for key in ("raw_file_bytes_acquired_in_this_study",
                "exact_hash_verified_locally", "raw_reanalysis_executed"):
        _require_false(source[key], key)
    limits = c["identification"]
    if (limits["seed_mass_total_package_effects_reported"] is not True or
            limits["whole_blossom_shade_effect_reported"] is not True or
            limits["gross_gas_exchange_greening_effect_observed"] is not True):
        raise ValueError("source-reported effects cannot be erased")
    if limits["no_cross_study_fitness_pooling"] is not True:
        raise ValueError("never pool unrelated Dalechampia study contexts")
    for key in (
        "bract_local_light_effect_isolated",
        "fruit_light_held_constant_during_shading",
        "light_equal_foil_sham_present",
        "bract_protection_constant_in_removal",
        "cause_of_seed_mass_effect_isolated_to_bract_carbon",
        "whole_organism_fitness_measured",
        "structural_architecture_BALANCE_occupancy_identified",
    ):
        _require_false(limits[key], key)
    if type(limits["new_independent_biological_clusters"]) is not int or limits["new_independent_biological_clusters"] != 0:
        raise ValueError("same original Dalechampia cluster cannot be counted anew")
    if c["next_stage"]["inferential_unit"] != "maternal plant clustered; blossom treatment allocation; seeds nested within blossom":
        raise ValueError("nested experimental units changed")
    return {
        "schema_version": SCHEMA,
        "status": "SOURCE_METHOD_CORRECTED_BRACT_CARBON_UNIDENTIFIED",
        "original_historical_treatment_codes": list(ARMS),
        "whole_blossom_foil_shade_includes_fruit_light": True,
        "bract_local_photosynthesis_only_intervention": False,
        "fruit_photosynthesis_in_whole_blossom_shade_isolated": False,
        "foil_specific_microclimate_control_available": False,
        "effect_on_four_week_seed_mass_as_total_treatment_package": True,
        "dryad_data_doi": c["dryad_doi"],
        "dryad_original_files": [
            {"file_id": n, "filename": FILE_IDENTITIES[n][0],
             "size_bytes": FILE_IDENTITIES[n][1], "md5": FILE_IDENTITIES[n][2]}
            for n in sorted(FILE_IDENTITIES)
        ],
        "historical_seed_count": dict(SOURCE_SEED_COUNTS),
        "historical_aborted_seed_count": dict(SOURCE_ABORTED_COUNTS),
        "raw_file_bytes_verified": False,
        "raw_reanalysis_executed": False,
        "structural_BALANCE_identified": False,
        "new_independent_biological_clusters": 0,
        "interpretation": (
            "bag = entire blossom shaded; cut = both bracts removed; "
            "cutcont = marginal edge-cut sham; not bract-local-only carbon effect"
        ),
    }


def _table(raw: bytes, expected_fields: list[str], label: str):
    """Parse byte-verified table; fail on ambiguous delimiter or missing headers."""
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        # Exact MD5 protects authenticity; historical text can use latin-1.
        text = raw.decode("latin-1")
    if not text.strip():
        raise ValueError(f"{label} empty verified source file")
    # These older Dryad .txt exports are delimited text; tolerate CRLF and BOM.
    sample = text[:4096]
    # The original archived files are tab-delimited. Sniffer may reject
    # an otherwise perfectly valid two-row TSV; a verified tab-separated
    # header is a stronger delimiter declaration than a heuristic guess.
    header = text.splitlines()[0]
    if "\t" in header:
        reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    else:
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters="\t,;")
        except csv.Error as exc:
            raise ValueError(f"{label} delimiter not resolved; review exact source layout") from exc
        reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    names = reader.fieldnames or []
    norm = lambda s: s.strip().casefold().replace("_", "").replace(" ", "")
    found = {norm(k): k for k in names if k is not None}
    if len(found) != len(names):
        raise ValueError(f"{label} duplicate header after normalization")
    if not set(map(norm, expected_fields)).issubset(found):
        missing = sorted(set(map(norm, expected_fields)).difference(found))
        raise ValueError(f"{label} missing source-documented columns: {missing}")
    rows = list(reader)
    if not rows or any(None in r for r in rows):
        raise ValueError(f"{label} empty records or unexpected field overflow")
    return rows, found, norm


def parse_source_decimal(value: object, label: str, *, allow_missing: bool = True) -> float | None:
    """Strict original numeric formatting: seed masses use decimal commas.

    Historical seed file 1 is Latin-1 tab-delimited with values such as
    "38,83". Gas-exchange file 2 uses periods. Neither convention allows a
    thousands separator, arbitrary comma stripping, imputation, or booleans.
    """
    if value is None:
        if allow_missing:
            return None
        raise ValueError(f"{label} cannot be missing")
    if not isinstance(value, str):
        raise ValueError(f"{label} must be original source text")
    raw = value.strip()
    if raw.casefold() in {"", "na", "nan", "null"}:
        if allow_missing:
            return None
        raise ValueError(f"{label} cannot be missing")
    if not re.fullmatch(r"[+-]?(?:\d+(?:[.,]\d+)?|\.\d+)", raw):
        raise ValueError(f"{label} invalid decimal format in original source")
    if "," in raw:
        raw = raw.replace(",", ".")
    try:
        out = float(raw)
    except (ValueError, OverflowError) as exc:
        raise ValueError(f"{label} not numeric") from exc
    if not math.isfinite(out):
        raise ValueError(f"{label} must be finite")
    return out


def _nonblank(row, found, normalized, label):
    x = row.get(found[normalized])
    if x is None or not str(x).strip() or str(x).strip().casefold() in {"nan", "na", "null"}:
        raise ValueError(f"missing {label} in exact-source raw row")
    return str(x).strip()


def verify_exact_dryad_bytes(contract: dict, file_bytes: dict[str, bytes]) -> dict:
    """Audit authentic file bytes and unit support; NO statistical model fit.

    Requires both exact original files, not filenames alone. Does not use
    the published 2015 n=1220 or 117 aborted as an imputation target.
    """
    metadata = audit_dalechampia_method_scope(contract)
    if not isinstance(file_bytes, dict) or set(file_bytes) != {
        f[0] for f in FILE_IDENTITIES.values()
    }:
        raise ValueError("both exact named original Dryad text files required")
    for filename, size, digest in FILE_IDENTITIES.values():
        data = file_bytes[filename]
        if type(data) is not bytes or len(data) != size:
            raise ValueError(f"{filename} source byte size differs from Dryad")
        if hashlib.md5(data).hexdigest() != digest:  # nosec: archival digest, not security
            raise ValueError(f"{filename} source MD5 differs from Dryad")
    f1=contract["dryad_source_files"][0]
    f2=contract["dryad_source_files"][1]
    by_file={item["source_file_id"]:item for item in (f1,f2)}
    rows, fields, normalize = _table(
        file_bytes[FILE_IDENTITIES[46163][0]], by_file[46163]["expected_fields"],
        "2015 seed mass file")
    row_counts: Counter[str] = Counter()
    flowers: dict[tuple[str, str], str] = {}
    plants: defaultdict[str, set[str]] = defaultdict(set)
    seen_seeds = set()
    missing_mass = 0
    nonmissing_by_arm = Counter()
    below_20_by_arm = Counter()
    for row in rows:
        female = _nonblank(row, fields, normalize("FemaleID"), "FemaleID")
        blossom = _nonblank(row, fields, normalize("crossID"), "crossID")
        code = _nonblank(row, fields, normalize("treatcode"), "treatcode").lower()
        seed_id = _nonblank(row, fields, normalize("seedID"), "seedID")
        if code not in ARMS:
            raise ValueError("unregistered source treatcode found")
        blossom_key = (female, blossom)
        if blossom_key in flowers and flowers[blossom_key] != code:
            raise ValueError("one blossom assigned to contradictory treatment arms")
        flowers[blossom_key] = code
        seed_key=(female, blossom, seed_id)
        if seed_key in seen_seeds:
            raise ValueError("duplicate seed within maternal plant and blossom")
        seen_seeds.add(seed_key)
        row_counts[code] += 1
        plants[code].add(female)
        m = parse_source_decimal(row.get(fields[normalize("seedmass")]),
                                 "seedmass")
        if m is None:
            missing_mass += 1
        else:
            if m < 0:
                raise ValueError("negative source seed mass")
            nonmissing_by_arm[code] += 1
            if m < 20.0:
                below_20_by_arm[code] += 1
    g_rows, g_fields, g_normalize = _table(
        file_bytes[FILE_IDENTITIES[46164][0]], by_file[46164]["expected_fields"],
        "2015 gas-exchange file")
    gas_units = set()
    for row in g_rows:
        plant=_nonblank(row,g_fields,g_normalize("Plant_ID"),"Plant_ID")
        replicate=_nonblank(row,g_fields,g_normalize("Replicate"),"Replicate")
        gas_units.add((plant,replicate))
    return {
        **metadata,
        "status": "EXACT_DRYAD_BYTES_VERIFIED_SUPPORT_ONLY_NO_MODELS",
        "raw_file_bytes_verified": True,
        "original_file_sha256": {
            k: hashlib.sha256(v).hexdigest() for k,v in sorted(file_bytes.items())
        },
        "raw_seed_records": len(rows),
        "raw_seed_missing_mass": missing_mass,
        "raw_treatment_seed_rows": dict(sorted(row_counts.items())),
        "raw_treatment_nonmissing_seed_mass_rows": {
            a: nonmissing_by_arm[a] for a in ARMS
        },
        "raw_treatment_numeric_mass_below_20_mg": {
            a: below_20_by_arm[a] for a in ARMS
        },
        "recorded_mass_counts_match_published_seeds": (
            dict(nonmissing_by_arm) == SOURCE_SEED_COUNTS
        ),
        "numeric_below_20_counts_match_published_abortions": (
            dict(below_20_by_arm) == SOURCE_ABORTED_COUNTS
        ),
        "morphological_abortions_independently_read_from_raw": False,
        "historical_seedmass_decimal_format": "LATIN1_TAB_DECIMAL_COMMA",
        "raw_treatment_maternal_plants": {
            a: len(plants[a]) for a in ARMS
        },
        "raw_independent_blossoms": len(flowers),
        "raw_independent_maternal_plants": len(set().union(*plants.values())),
        "raw_gas_exchange_rows": len(g_rows),
        "raw_gas_exchange_plant_replicate_units": len(gas_units),
        "raw_row_counts_equal_published_total_per_arm": dict(row_counts) == SOURCE_SEED_COUNTS,
        "published_abortions_reconstructed": False,
        "source_original_mixed_model_reproduced": False,
        "raw_reanalysis_executed": False,
        "interpretation": "raw source identity and nested measurement support verified; statistical analysis not performed",
    }
