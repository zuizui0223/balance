"""Guards for the Vallejo-Marin-2010 heteranthery family discovery universe."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


FIELDS = (
    "u3_record_id",
    "universe_id",
    "family",
    "order_apg3",
    "review_source",
    "review_doi",
    "heteranthery_status",
    "family_confirmation_basis",
    "representative_taxa",
    "representative_taxa_status",
    "analysis_role",
    "matched_control_status",
    "notes",
)

EXPECTED_FAMILIES = {
    "Pontederiaceae",
    "Haemodoraceae",
    "Commelinaceae",
    "Tecophilaeaceae",
    "Dilleniaceae",
    "Lythraceae",
    "Melastomataceae",
    "Anacardiaceae",
    "Malvaceae",
    "Bixaceae",
    "Brassicaceae",
    "Fabaceae",
    "Malpighiaceae",
    "Lecythidaceae",
    "Solanaceae",
    "Scrophulariaceae",
}

EXPECTED_ORDERS = {
    "Asparagales",
    "Brassicales",
    "Commelinales",
    "Dilleniales",
    "Ericales",
    "Fabales",
    "Lamiales",
    "Malpighiales",
    "Malvales",
    "Myrtales",
    "Sapindales",
    "Solanales",
}

REP_STATUS = {"BODY_TEXT_NAMED", "TABLE_S1_REPRESENTATIVE_PENDING"}


def load_u3_universe(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("U3 universe columns must match canonical order")
        rows = list(reader)

    if len(rows) != 16:
        raise ValueError("U3 review-defined family universe must contain exactly 16 families")

    ids = set()
    families = set()
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside U3 schema")
        for field in FIELDS[:-1]:
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"row {n} {field} must be frozen")
        if row["u3_record_id"] in ids:
            raise ValueError(f"duplicate U3 record id {row['u3_record_id']!r}")
        ids.add(row["u3_record_id"])
        if row["family"] in families:
            raise ValueError(f"duplicate U3 family {row['family']!r}")
        families.add(row["family"])
        if row["universe_id"] != "U3_VALLEJOMARIN_2010":
            raise ValueError(f"row {n} wrong universe_id")
        if row["review_doi"] != "10.1111/j.1469-8137.2010.03430.x":
            raise ValueError(f"row {n} wrong review DOI")
        if row["heteranthery_status"] != "PRESENT":
            raise ValueError(f"row {n} U3 is a review-defined heteranthery-positive family surface")
        if row["family_confirmation_basis"] != "FIGURE2":
            raise ValueError(f"row {n} family membership must be tied to Figure 2")
        if row["representative_taxa_status"] not in REP_STATUS:
            raise ValueError(f"row {n} invalid representative_taxa_status")
        if row["analysis_role"] != "POSITIVE_ARCHITECTURE_DISCOVERY_ONLY":
            raise ValueError(f"row {n} U3 must not be promoted to a denominator")
        if row["matched_control_status"] != "CONTROL_NOT_REGISTERED":
            raise ValueError(f"row {n} controls must be registered in a separate matched-control layer")

    if families != EXPECTED_FAMILIES:
        missing = sorted(EXPECTED_FAMILIES - families)
        extra = sorted(families - EXPECTED_FAMILIES)
        raise ValueError(f"U3 family set drift: missing={missing}, extra={extra}")

    orders = {r["order_apg3"] for r in rows}
    if orders != EXPECTED_ORDERS:
        raise ValueError(
            f"U3 must span the 12 review-reported orders; got {sorted(orders)}"
        )
    return rows


def build_u3_readout_from_rows(rows: list[dict[str, str]]) -> dict:
    rep = Counter(r["representative_taxa_status"] for r in rows)
    orders = Counter(r["order_apg3"] for r in rows)
    return {
        "analysis": "balance_plant_u3_heteranthery_family_universe",
        "n_family_cases": len(rows),
        "n_orders": len(orders),
        "order_counts": dict(sorted(orders.items())),
        "representative_taxa_status_counts": dict(sorted(rep.items())),
        "n_body_text_representative_families": rep.get("BODY_TEXT_NAMED", 0),
        "n_table_s1_representative_pending": rep.get("TABLE_S1_REPRESENTATIVE_PENDING", 0),
        "matched_control_layer_ready": False,
        "confirmatory_denominator_ready": False,
        "claim_ceiling": (
            "review_defined_heteranthery_positive_family_discovery_only_"
            "not_prevalence_not_case_control_until_matched_controls_registered"
        ),
    }


def build_u3_readout(path: Path) -> dict:
    return build_u3_readout_from_rows(load_u3_universe(path))
