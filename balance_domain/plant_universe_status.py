"""Cross-universe readiness ledger for the BALANCE plant macro programme."""
from __future__ import annotations

import csv
from pathlib import Path


FIELDS = (
    "universe_id",
    "literature_family",
    "sampling_role",
    "unit_grain",
    "registered_units",
    "target_units",
    "source_closed",
    "outcome_blind_architecture_sampling",
    "double_code_ready",
    "analysis_role",
    "current_blocker",
    "claim_ceiling",
)

EXPECTED = {
    "U1_HAAS_LORTIE_2020",
    "U2_BARRETT_2002",
    "U3_VALLEJOMARIN_2010",
}


def _bool(value: str, field: str, row: int) -> bool:
    v = value.strip().casefold()
    if v not in {"true", "false"}:
        raise ValueError(f"row {row} {field} must be literal true or false")
    return v == "true"


def load_plant_universe_status(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("plant universe status columns must match canonical order")
        rows = list(reader)

    if {r["universe_id"] for r in rows} != EXPECTED:
        raise ValueError("plant universe status must register exactly U1, U2 and U3")

    out = []
    for n, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {n} has fields outside status schema")
        clean = dict(row)
        for field in (
            "universe_id", "literature_family", "sampling_role", "unit_grain",
            "analysis_role", "current_blocker", "claim_ceiling",
        ):
            if not clean[field].strip():
                raise ValueError(f"row {n} {field} must be frozen")
        for field in ("registered_units", "target_units"):
            try:
                clean[field] = int(clean[field])
            except ValueError as exc:
                raise ValueError(f"row {n} {field} must be integer") from exc
            if clean[field] <= 0:
                raise ValueError(f"row {n} {field} must be positive")
        for field in (
            "source_closed",
            "outcome_blind_architecture_sampling",
            "double_code_ready",
        ):
            clean[field] = _bool(clean[field], field, n)

        if clean["registered_units"] > clean["target_units"]:
            raise ValueError(f"row {n} registered_units cannot exceed target_units")
        out.append(clean)

    by_id = {r["universe_id"]: r for r in out}
    u1, u2, u3 = (
        by_id["U1_HAAS_LORTIE_2020"],
        by_id["U2_BARRETT_2002"],
        by_id["U3_VALLEJOMARIN_2010"],
    )

    if u1["source_closed"] or u1["double_code_ready"]:
        raise ValueError("U1 cannot close before the full 47-taxon review universe is reconciled")
    if not u1["outcome_blind_architecture_sampling"]:
        raise ValueError("U1 must remain outcome-blind")

    if not (u2["source_closed"] and u2["outcome_blind_architecture_sampling"]):
        raise ValueError("U2 is the source-closed outcome-blind review universe")
    if not u2["double_code_ready"]:
        raise ValueError("U2 first-20 source packet is already ready for independent double coding")

    if not u3["source_closed"]:
        raise ValueError("U3 16-family Figure-2 membership is source-closed")
    if u3["outcome_blind_architecture_sampling"]:
        raise ValueError("U3 is selected on heteranthery presence and must not be called outcome-blind")
    if u3["double_code_ready"]:
        raise ValueError("U3 requires species cases and matched controls before double coding")

    return out


def build_plant_universe_status(path: Path) -> dict:
    rows = load_plant_universe_status(path)
    by_id = {r["universe_id"]: r for r in rows}
    return {
        "analysis": "balance_plant_macro_universe_status",
        "n_registered_universes": len(rows),
        "source_closed_universes": sorted(
            r["universe_id"] for r in rows if r["source_closed"]
        ),
        "outcome_blind_universes": sorted(
            r["universe_id"] for r in rows if r["outcome_blind_architecture_sampling"]
        ),
        "double_code_ready_universes": sorted(
            r["universe_id"] for r in rows if r["double_code_ready"]
        ),
        "u1_completion_fraction": (
            by_id["U1_HAAS_LORTIE_2020"]["registered_units"]
            / by_id["U1_HAAS_LORTIE_2020"]["target_units"]
        ),
        "claim_ceiling": (
            "programme_readiness_only_not_empirical_effect_not_prevalence_"
            "not_conflict_resolution_result"
        ),
    }
