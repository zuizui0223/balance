"""Outcome-blind exact-species dependence skeleton across U1, U2 and U3."""
from __future__ import annotations

import csv
import re
from pathlib import Path


OVERLAP_FIELDS = (
    "canonical_taxon",
    "occurrence_count",
    "universe_membership",
    "occurrence_ids",
    "dependence_kind",
    "u3_dependence_block",
    "dependence_rule",
)

DEPENDENCE_RULE = "CLUSTER_SAME_TAXON_DO_NOT_COUNT_AS_INDEPENDENT"


def canonicalize_taxon(value: str) -> str:
    value = re.sub(r"\s*\([^)]*\)\s*$", "", value.strip())
    return " ".join(value.split()).casefold()


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_occurrences(
    u1_path: Path,
    u2_path: Path,
    u3_cases_path: Path,
    u3_pairs_path: Path,
    u3_dependence_path: Path,
) -> list[dict[str, str]]:
    occurrences: list[dict[str, str]] = []

    for row in _rows(u1_path):
        occurrences.append(
            {
                "canonical_taxon": canonicalize_taxon(row["taxon_raw"]),
                "display_taxon": re.sub(r"\s*\([^)]*\)\s*$", "", row["taxon_raw"]).strip(),
                "universe": "U1",
                "role": "REVIEW_TAXON",
                "occurrence_id": row["universe_record_id"],
                "u3_dependence_block": "",
            }
        )

    for row in _rows(u2_path):
        occurrences.append(
            {
                "canonical_taxon": canonicalize_taxon(row["taxon_raw"]),
                "display_taxon": re.sub(r"\s*\([^)]*\)\s*$", "", row["taxon_raw"]).strip(),
                "universe": "U2",
                "role": "REVIEW_TAXON",
                "occurrence_id": row["universe_record_id"],
                "u3_dependence_block": "",
            }
        )

    dependence = _rows(u3_dependence_path)
    block_by_case = {r["case_taxon"]: r["dependence_block_id"] for r in dependence}
    block_by_pair = {r["pair_id"]: r["dependence_block_id"] for r in dependence}

    for row in _rows(u3_cases_path):
        taxon = row["case_taxon"].strip()
        occurrences.append(
            {
                "canonical_taxon": canonicalize_taxon(taxon),
                "display_taxon": taxon,
                "universe": "U3_CASE",
                "role": "MATCHED_CASE",
                "occurrence_id": row["case_id"],
                "u3_dependence_block": block_by_case.get(taxon, ""),
            }
        )

    for row in _rows(u3_pairs_path):
        taxon = row["control_taxon"].strip()
        occurrences.append(
            {
                "canonical_taxon": canonicalize_taxon(taxon),
                "display_taxon": taxon,
                "universe": "U3_CONTROL",
                "role": "MATCHED_CONTROL",
                "occurrence_id": f'{row["pair_id"]}:CONTROL',
                "u3_dependence_block": block_by_pair.get(row["pair_id"], ""),
            }
        )

    return occurrences


def build_cross_universe_dependence_readout(
    u1_path: Path,
    u2_path: Path,
    u3_cases_path: Path,
    u3_pairs_path: Path,
    u3_dependence_path: Path,
) -> dict:
    occurrences = build_occurrences(
        u1_path, u2_path, u3_cases_path, u3_pairs_path, u3_dependence_path
    )
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in occurrences:
        grouped.setdefault(row["canonical_taxon"], []).append(row)

    repeated = {k: v for k, v in grouped.items() if len(v) > 1}
    cross_universe = {
        k: v
        for k, v in repeated.items()
        if len({r["universe"] for r in v}) > 1
        and not {r["universe"] for r in v} == {"U3_CASE", "U3_CONTROL"}
    }

    receipts = []
    for key, rows in sorted(repeated.items()):
        universes = sorted({r["universe"] for r in rows})
        kind = (
            "REUSED_CONTROL_SAME_SPECIES"
            if set(universes) == {"U3_CONTROL"}
            else "CROSS_UNIVERSE_SAME_SPECIES"
        )
        receipts.append(
            {
                "canonical_taxon": key,
                "display_taxon": sorted(
                    {r["display_taxon"] for r in rows}, key=str.casefold
                )[0],
                "occurrence_count": len(rows),
                "universe_membership": universes,
                "occurrence_ids": sorted(r["occurrence_id"] for r in rows),
                "dependence_kind": kind,
                "u3_dependence_blocks": sorted(
                    {r["u3_dependence_block"] for r in rows if r["u3_dependence_block"]}
                ),
            }
        )

    return {
        "analysis": "balance_plant_cross_universe_exact_species_dependence_v2",
        "n_occurrence_rows": len(occurrences),
        "n_unique_canonical_taxa": len(grouped),
        "n_repeated_exact_taxon_groups": len(repeated),
        "n_cross_universe_same_species_groups": len(cross_universe),
        "repeated_taxon_receipts": receipts,
        "dependence_rule": DEPENDENCE_RULE,
        "outcome_blind": True,
        "claim_ceiling": (
            "exact_species_reuse_and_u3_shared_control_dependence_only_"
            "not_phylogenetic_covariance_not_final_model_membership_not_effect_estimate"
        ),
    }


def load_overlap_registry(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != OVERLAP_FIELDS:
            raise ValueError("cross-universe overlap registry columns must match canonical order")
        rows = list(reader)
    if not rows:
        raise ValueError("cross-universe overlap registry must not be empty")
    for n, row in enumerate(rows, start=2):
        if row["dependence_rule"] != DEPENDENCE_RULE:
            raise ValueError(f"row {n} dependence rule drift")
        if int(row["occurrence_count"]) < 2:
            raise ValueError(f"row {n} overlap must contain at least two occurrences")
    return rows


def validate_overlap_registry(
    registry_path: Path,
    u1_path: Path,
    u2_path: Path,
    u3_cases_path: Path,
    u3_pairs_path: Path,
    u3_dependence_path: Path,
) -> dict:
    registry = load_overlap_registry(registry_path)
    readout = build_cross_universe_dependence_readout(
        u1_path, u2_path, u3_cases_path, u3_pairs_path, u3_dependence_path
    )
    computed = {
        r["canonical_taxon"]: r for r in readout["repeated_taxon_receipts"]
    }
    registered = {r["canonical_taxon"]: r for r in registry}
    if set(computed) != set(registered):
        raise ValueError(
            f"overlap registry drift: computed={sorted(computed)}, "
            f"registered={sorted(registered)}"
        )
    for key, row in registered.items():
        receipt = computed[key]
        if int(row["occurrence_count"]) != receipt["occurrence_count"]:
            raise ValueError(f"{key} occurrence count drift")
        if row["universe_membership"].split(";") != receipt["universe_membership"]:
            raise ValueError(f"{key} universe membership drift")
        if row["occurrence_ids"].split(";") != receipt["occurrence_ids"]:
            raise ValueError(f"{key} occurrence id drift")
        expected_blocks = ";".join(receipt["u3_dependence_blocks"])
        if row["u3_dependence_block"] != expected_blocks:
            raise ValueError(f"{key} U3 dependence block drift")
        if row["dependence_kind"] != receipt["dependence_kind"]:
            raise ValueError(f"{key} dependence kind drift")
    return readout
