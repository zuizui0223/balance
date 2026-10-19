"""Independent species-first structural-opportunity screen from AusTraits v7.

The observable is *sexual system or floral morphology*, not a measured conflict,
costed modular fitness contrast, or historical structural-origin event.

All source-derived statuses remain distinct from SCH, BALANCE V4 and BITA
evidence. Report raw/qualified denominators, source conflict, and genus support.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import tempfile
import zipfile

from . import island_austraits_fetch as source

SOURCE_NAME = "AusTraits"
SOURCE_VERSION = "7.0.0"
SELECTED_TRAITS = {
    "sex_type",
    "flower_structural_sex_type",
    "flower_perianth_fusion",
    "flower_perianth_symmetry",
    "pollination_syndrome",
    "pollination_system",
}
SEX_MODES = {
    "hermaphrodite": "SHARED_SEX_SYSTEM",
    "monoecious": "SEX_SEPARATED_AMONG_FLOWERS",
    "dioecious": "SEX_SEPARATED_AMONG_INDIVIDUALS",
}
POLLEN = {
    "wind": "WIND",
    "insect": "INSECT",
}
BINOMIAL = re.compile(r"^[A-Z][a-z-]+ [a-z-]+$")

def _version(v: object) -> str:
    return str(v or "").lstrip("v").strip()

def select_frozen_release(payload: dict) -> dict:
    hits = source._release_hits(payload)
    matches = [r for r in hits if _version(
        (r.get("metadata") or {}).get("version")
    ) == SOURCE_VERSION]
    if len(matches) != 1:
        raise ValueError(f"Require exactly one AusTraits {SOURCE_VERSION} release; found {len(matches)}")
    return matches[0]

def _source_rows(source_csv: Path) -> list[dict[str, str]]:
    with source_csv.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or set(rows[0]) != {
        "taxon_name", "trait_name", "trait_value", "trait_unit",
        "dataset_key", "source_record_id"
    }:
        raise ValueError("Wrong standardized public source schema")
    ids = [r["source_record_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Source record IDs not unique")
    if any(
        r["trait_name"] not in SELECTED_TRAITS
        or not r["dataset_key"]
        or not r["taxon_name"]
        or not r["trait_value"]
        for r in rows
    ):
        raise ValueError("Incomplete raw trait, dataset or value")
    return rows

def _safe_species_value(rows: list[dict[str, str]], trait: str, allowed: dict) -> tuple[dict[str, str], dict]:
    """Only one stable exact label per binomial; conflict/unknowns excluded."""
    by_species: dict[str, set[str]] = defaultdict(set)
    seen: set[str] = set()
    n_nonbinomial = 0
    for r in rows:
        if r["trait_name"] != trait:
            continue
        name = r["taxon_name"]
        if not BINOMIAL.fullmatch(name):
            n_nonbinomial += 1
            continue
        seen.add(name)
        by_species[name].add(r["trait_value"].strip().lower())
    accepted = {}
    unknown = 0
    conflict = 0
    for name, values in by_species.items():
        if len(values) != 1:
            conflict += 1
        else:
            only = next(iter(values))
            if only in allowed:
                accepted[name] = allowed[only]
            else:
                unknown += 1
    return accepted, {
        "observed_exact_binomial_species": len(seen),
        "accepted_species": len(accepted),
        "multiple_raw_labels_excluded": conflict,
        "unmapped_single_raw_label_species": unknown,
        "non_binomial_source_rows_excluded": n_nonbinomial,
        "allowed_exact_labels": dict(allowed),
    }

def _categorical_counts(raw: list[dict[str, str]], trait: str) -> dict:
    values = Counter(r["trait_value"].strip().lower() for r in raw if r["trait_name"] == trait)
    datasets = Counter(r["dataset_key"] for r in raw if r["trait_name"] == trait)
    species = {r["taxon_name"] for r in raw if r["trait_name"] == trait}
    return {
        "source_rows": sum(values.values()),
        "distinct_taxon_names": len(species),
        "top_raw_labels": dict(values.most_common(20)),
        "top_source_datasets": dict(datasets.most_common(20)),
    }

def _pair_analysis(rows: list[dict[str, str]], *, minimum_per_arm: int = 20,
                   minimum_genera_per_arm: int = 5) -> dict:
    sex, sx = _safe_species_value(rows, "sex_type", SEX_MODES)
    pollen, pol = _safe_species_value(rows, "pollination_syndrome", POLLEN)
    # Pollination system is not silently interpreted as the same estimand as
    # syndrome. The supplementary source remains in coverage metadata only.
    paired = {s: (sex[s], pollen[s]) for s in sorted(sex.keys() & pollen.keys())}
    arms: dict[str, list[str]] = defaultdict(list)
    for name, (_, pollen_mode) in paired.items():
        arms[pollen_mode].append(name)
    groups = {k: len(set(s.split()[0] for s in names)) for k, names in arms.items()}
    cross = Counter(f"{mode} | {sex_mode}" for sex_mode, mode in paired.values())
    enough = all(len(arms.get(mode, [])) >= minimum_per_arm
                 and groups.get(mode, 0) >= minimum_genera_per_arm
                 for mode in ("INSECT", "WIND"))

    def separated_fraction(names: list[str]) -> float | None:
        if not names:
            return None
        return sum(sex[n] != "SHARED_SEX_SYSTEM" for n in names) / len(names)

    # Within-genus comparison requires the SAME genus with both wind and
    # insect states. It is a descriptive contrast, not a phylogenetically
    # calibrated causal effect.
    genus_pair: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for name, (_, mode) in paired.items():
        genus_pair[name.split()[0]][mode].append(name)
    mixed = [
        genus for genus, arms2 in genus_pair.items()
        if arms2.get("INSECT") and arms2.get("WIND")
    ]
    within = [
        separated_fraction(genus_pair[genus]["WIND"])
        - separated_fraction(genus_pair[genus]["INSECT"])
        for genus in mixed
    ]
    return {
        "estimand": "descriptive species sexual-system separation by exact raw pollen-syndrome insect vs wind",
        "status": "EXPLORATORY_DESCRIPTIVE_COMPARISON" if enough else "HOLD_INSUFFICIENT_COMMON_SUPPORT",
        "source_species_denominator": sx,
        "pollen_syndrome_source_denominator": pol,
        "qualified_exact_species_overlap": len(paired),
        "by_pollen_mode": {
            mode: {
                "species": len(arms.get(mode, [])),
                "genera": groups.get(mode, 0),
                "sex_separated_fraction": separated_fraction(arms.get(mode, [])),
            }
            for mode in ("INSECT", "WIND")
        },
        "sex_system_by_mode": dict(sorted(cross.items())),
        "raw_difference_wind_minus_insect": (
            separated_fraction(arms["WIND"]) - separated_fraction(arms["INSECT"])
            if enough else None
        ),
        "genera_with_both_pollen_modes": len(mixed),
        "mean_within_genus_difference": sum(within) / len(within) if within else None,
        "not_a_pooled_random_effect_or_causal_parameter": True,
    }

def analyze_selected_csv(selected_csv: Path, manifest: dict) -> dict:
    raw = _source_rows(selected_csv)
    if not manifest.get("archive_checksum_verified"):
        raise ValueError("Cannot analyze unverified public archive bytes")
    if _version(manifest.get("release_version")) != SOURCE_VERSION:
        raise ValueError("AusTraits source release mismatch")
    if set(manifest.get("requested_trait_names", [])) != SELECTED_TRAITS:
        raise ValueError("Selected trait list differs from frozen source contract")
    coverage = {t: _categorical_counts(raw,t) for t in sorted(SELECTED_TRAITS)}
    result = {
        "schema": "BALANCE_AUSTRAITS_INDEPENDENT_STRUCTURAL_OPPORTUNITY_V1",
        "status": "OPEN_PUBLIC_TRAIT_COVERAGE_NOT_DIRECT_CONFLICT",
        "source": SOURCE_NAME,
        "release_version": SOURCE_VERSION,
        "release_doi": manifest.get("doi"),
        "archive_sha256": manifest.get("archive_sha256"),
        "archive_checksum_verified": True,
        "standardized_selected_rows": len(raw),
        "source_name_coverage": len({r["taxon_name"] for r in raw}),
        "trait_coverage": coverage,
        "sex_system_pollination_syndrome_pilot": _pair_analysis(raw),
        "interpretation": {
            "sex_type": "species reproductive sex system (not direct trait conflict or module construction cost)",
            "flower_structural_sex_type": "flower-level structural status (not identical to species sex system)",
            "flower_perianth_fusion": "perianth morphology, not identified functional modularity",
            "pollination_syndrome": "source-coded opportunity/syndrome, not a direct agent fitness gradient",
        },
        "caution": [
            "not an unbiased random angiosperm sample; trait coverage and source availability are nonrandom",
            "same-species trait joining is descriptive; no experimental conflict-on/off intervention",
            "data labels are not phylogenetically independent",
            "no direct W_D-W_S structural worldline, fitness cost K or historical transition",
            "same raw source records may underlie multiple trait values; no independent replication claim",
            "no source data are redistributed in the analysis receipt",
        ],
    }
    return result

def fetch_and_analyze(output_dir: Path) -> dict:
    """Fetch a checksum-verified fixed AusTraits version and emit summary only."""
    output_dir.mkdir(parents=True,exist_ok=True)
    # Source selection must precede archive downloading or outcome inspection.
    versions = source._request_json(source.VERSIONS_API)
    release = select_frozen_release(versions)
    archive = source.select_plain_text_archive(release)
    metadata = release.get("metadata") or {}
    if not str(archive.get("checksum", "")).strip():
        raise ValueError("Missing Zenodo declared source checksum")
    with tempfile.TemporaryDirectory(prefix="balance_austraits_independent_") as root:
        tmp = Path(root)
        saved = tmp / str(archive["key"])
        source._download(str(archive["url"]), saved)
        verified = source._verify_declared_checksum(saved, str(archive["checksum"]))
        digest = source._file_digest(saved,"sha256")
        with zipfile.ZipFile(saved) as zf:
            if any(
                Path(p.filename).is_absolute() or ".." in Path(p.filename).parts
                for p in zf.infolist()
            ):
                raise ValueError("Unsafe archive member path")
            zf.extractall(tmp / "archive")
        table, columns = source.discover_long_trait_table(tmp / "archive")
        selected = tmp / "selected.csv"
        stats = source.standardize_dataset(
            table, selected, columns=columns, dataset_key=None,
            trait_names=SELECTED_TRAITS,
        )
        manifest = {
            "release_version": metadata.get("version"),
            "doi": metadata.get("doi"),
            "release_record_id": release.get("id"),
            "archive_key": archive["key"],
            "archive_checksum_verified": verified,
            "archive_declared_checksum": archive["checksum"],
            "archive_sha256": digest,
            "requested_trait_names": sorted(SELECTED_TRAITS),
            "discovered_columns": columns,
            **stats,
        }
        result = analyze_selected_csv(selected, manifest)
    (output_dir / "austraits_structural_opportunity_manifest.json").write_text(
        json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    (output_dir / "austraits_structural_opportunity_readout.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    return result
