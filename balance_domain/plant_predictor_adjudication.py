"""Independent adjudication return contract for BALANCE plant predictor receipts."""
from __future__ import annotations

from pathlib import Path

from .plant_confirmatory import load_plant_predictor_receipts


IMMUTABLE_RECEIPT_FIELDS = (
    "receipt_id",
    "cluster_id",
    "predictor",
    "reported_value",
    "source_id",
    "notes",
)

FINAL_STATUSES = {"ADJUDICATED", "REJECTED"}


def validate_predictor_adjudication_return(
    frozen_rows: list[dict[str, str]],
    reviewed_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Require reviewed receipts to preserve the frozen source-screened claim.

    Review may accept/reject the receipt and may refine evidence_type or
    outcome_independence. It may not rewrite the screened predictor value or source
    provenance. A wrong/unsupported value is rejected rather than edited in place.
    """
    frozen = {row["receipt_id"]: row for row in frozen_rows}
    reviewed = {row["receipt_id"]: row for row in reviewed_rows}

    if len(frozen) != len(frozen_rows):
        raise ValueError("frozen predictor receipt ledger contains duplicate receipt_id")
    if len(reviewed) != len(reviewed_rows):
        raise ValueError("reviewed predictor receipt ledger contains duplicate receipt_id")
    if set(reviewed) != set(frozen):
        raise ValueError(
            "reviewed predictor receipt IDs must exactly match the frozen receipt frame"
        )

    out = []
    for receipt_id in sorted(frozen):
        before = frozen[receipt_id]
        after = reviewed[receipt_id]

        for field in IMMUTABLE_RECEIPT_FIELDS:
            if after[field] != before[field]:
                raise ValueError(
                    f"predictor receipt {receipt_id!r} cannot modify frozen {field}"
                )

        if after["adjudication_status"] not in FINAL_STATUSES:
            raise ValueError(
                f"predictor receipt {receipt_id!r} review must end ADJUDICATED or REJECTED"
            )

        if after["adjudication_status"] == "ADJUDICATED":
            if after["reported_value"] == "UNRESOLVED":
                raise ValueError(
                    f"predictor receipt {receipt_id!r} cannot adjudicate UNRESOLVED value"
                )
            if after["outcome_independence"] != "TRUE":
                raise ValueError(
                    f"predictor receipt {receipt_id!r} ADJUDICATED requires "
                    "outcome_independence=TRUE"
                )
            if after["evidence_type"] in {"OUTCOME_DERIVED", "UNCLEAR"}:
                raise ValueError(
                    f"predictor receipt {receipt_id!r} ADJUDICATED requires "
                    "source-side evidence type"
                )

        out.append(after)

    return out


def load_predictor_adjudication_return(
    reviewed_path: Path,
    frozen_path: Path,
) -> list[dict[str, str]]:
    frozen = load_plant_predictor_receipts(frozen_path)
    reviewed = load_plant_predictor_receipts(reviewed_path)
    return validate_predictor_adjudication_return(frozen, reviewed)


def build_predictor_adjudication_readout(
    reviewed_path: Path,
    frozen_path: Path,
) -> dict:
    rows = load_predictor_adjudication_return(reviewed_path, frozen_path)
    adjudicated = [row for row in rows if row["adjudication_status"] == "ADJUDICATED"]
    rejected = [row for row in rows if row["adjudication_status"] == "REJECTED"]
    clusters = sorted({row["cluster_id"] for row in rows})
    complete_clusters = sorted(
        cluster
        for cluster in clusters
        if sum(
            row["cluster_id"] == cluster
            and row["adjudication_status"] == "ADJUDICATED"
            for row in rows
        ) == 3
    )
    return {
        "analysis": "balance_plant_predictor_receipt_adjudication_return",
        "n_receipts": len(rows),
        "n_adjudicated": len(adjudicated),
        "n_rejected": len(rejected),
        "n_clusters": len(clusters),
        "n_clusters_with_three_adjudicated_receipts": len(complete_clusters),
        "clusters_with_three_adjudicated_receipts": complete_clusters,
        "frozen_values_and_source_provenance_preserved": True,
        "claim_ceiling": "predictor_receipt_review_only_no_architecture_effect",
    }
