"""Fail-closed source eligibility audit for structural BALANCE worldline studies.

This is NOT a fitness estimator. It requires *one and the same biological
context* to identify SCH conflict and optimize both net structural architectures
on a commensurable reproductive/growth-fitness scale with joint uncertainty.

Cross-paper collage, functional ON/OFF toggles, uncosted nested option sets,
and morphological proxies cannot be promoted to a direct structural receipt.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping


SCHEMA = "BALANCE_STRUCTURAL_WORLDLINE_SOURCE_AUDIT_V1"
COMPARATORS = (
    "FUNCTIONAL_STATE_ONLY",
    "STRUCTURAL_NONNESTED",
    "STRUCTURAL_NESTED_NET_COSTED",
    "NESTED_UNCOSTED_ENVELOPE",
    "STRUCTURAL_COMPARATOR_UNRESOLVED",
)
EVIDENCE_KEYS = (
    "positive_sch_conflict_on_fitness_scale",
    "matched_shared_structural_worldline",
    "matched_alternative_structural_worldline",
    "same_biological_context",
    "common_net_whole_system_fitness_scale",
    "preoutcome_accessibility_and_comparator_frozen",
    "joint_uncertainty_on_worldline_difference",
    "structural_intervention_or_architecture_identity_verified",
    "source_lineage_and_independent_replication_verified",
)
STATE_VERIFIED = "SOURCE_VERIFIED"
STATE_MISSING = "NOT_IDENTIFIED_IN_AUDITED_SOURCE"


@dataclass(frozen=True)
class StructuralSourceAudit:
    candidate_id: str
    status: str
    comparator_class: str
    missing_gates: tuple[str, ...]
    analysis_kind: str = "SOURCE_ELIGIBILITY_ONLY_NOT_EMPIRICAL_WORLDLINE"
    balance_occupancy_identified: bool = False
    structural_architecture_cost_identified_by_audit: bool = False
    direct_worldline_gap_estimated: bool = False
    contributes_new_independent_biological_cluster: bool = False


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text")
    return value.strip()


def adjudicate_structural_source(row: Mapping[str, object]) -> StructuralSourceAudit:
    """Validate a source-annotated candidate; never synthesize missing fitness.

    SOURCE_VERIFIED is a curator assertion with an explanatory source excerpt,
    not independent authentication of the article or data. Actual promotion
    still needs the original source data, preregistration and estimator receipt.
    """
    if not isinstance(row, dict):
        raise ValueError("candidate record must be a mapping")
    expected = {
        "candidate_id", "system", "source_doi", "source_url",
        "comparison_class", "net_architecture_cost_in_fitness",
        "observed_anchor", "evidence", "same_cluster_as",
    }
    if set(row) != expected:
        raise ValueError("candidate fields differ from the frozen audit schema")
    ident = _text(row["candidate_id"], "candidate_id")
    _text(row["system"], "system")
    doi = _text(row["source_doi"], "source_doi")
    if not doi.startswith("10.") or "/" not in doi:
        raise ValueError("source_doi must be a DOI")
    url = _text(row["source_url"], "source_url")
    if not url.startswith("https://"):
        raise ValueError("source_url must be HTTPS")
    _text(row["observed_anchor"], "observed_anchor")
    _text(row["same_cluster_as"], "same_cluster_as")
    klass = _text(row["comparison_class"], "comparison_class")
    if klass not in COMPARATORS:
        raise ValueError("unknown comparator_class")
    if type(row["net_architecture_cost_in_fitness"]) is not bool:
        raise ValueError("net_architecture_cost_in_fitness must be boolean")
    evidence = row["evidence"]
    if not isinstance(evidence, dict) or set(evidence) != set(EVIDENCE_KEYS):
        raise ValueError("incomplete source-evidence field set")

    missing: list[str] = []
    for key in EVIDENCE_KEYS:
        item = evidence[key]
        if not isinstance(item, dict) or set(item) != {"status", "source_basis"}:
            raise ValueError(f"{key} requires status and source_basis")
        state = item["status"]
        if state not in (STATE_VERIFIED, STATE_MISSING):
            raise ValueError(f"{key} has unsupported evidence status")
        _text(item["source_basis"], f"{key}.source_basis")
        if state != STATE_VERIFIED:
            missing.append(key)

    if klass in ("FUNCTIONAL_STATE_ONLY", "NESTED_UNCOSTED_ENVELOPE",
                 "STRUCTURAL_COMPARATOR_UNRESOLVED"):
        missing.append("NOT_A_REGISTERED_NET_STRUCTURAL_COMPARATOR")
    if klass == "STRUCTURAL_NESTED_NET_COSTED":
        # The native uncosted superset cannot be worse than its subset.
        # A net structural gap needs an explicit verified cost on that scale.
        if row["net_architecture_cost_in_fitness"] is not True:
            missing.append("MISSING_NET_NESTED_ARCHITECTURE_COST")
    if klass == "STRUCTURAL_NONNESTED" and row["net_architecture_cost_in_fitness"]:
        # Non-nested states may already have net costs embedded in their
        # directly measured, whole-system reproductive or growth fitness.
        pass

    return StructuralSourceAudit(
        candidate_id=ident,
        comparator_class=klass,
        status=("SOURCE_COMPARATOR_ELIGIBLE_FOR_WORLDLINE_TEST_NOT_BALANCE"
                if not missing else "SOURCE_COMPARATOR_HOLD"),
        missing_gates=tuple(missing),
    )


def adjudicate_structural_registry(registry: Mapping[str, object]) -> dict:
    """Make a deterministic audit result without counting pattern-ledger rows."""
    if not isinstance(registry, dict) or set(registry) != {
        "schema_version", "status", "candidates"
    }:
        raise ValueError("source registry schema mismatch")
    if registry.get("schema_version") != SCHEMA:
        raise ValueError("source registry schema_version mismatch")
    if registry.get("status") != "CURATED_SOURCE_AUDIT_NOT_FIELD_DATA":
        raise ValueError("source registry is not a curated audit")
    records = registry.get("candidates")
    if not isinstance(records, list) or not records:
        raise ValueError("non-empty source candidate registry required")
    results = []
    seen = set()
    for candidate in records:
        result = adjudicate_structural_source(candidate)
        if result.candidate_id in seen:
            raise ValueError("duplicate candidate_id")
        seen.add(result.candidate_id)
        normalized = asdict(result)
        # JSON readers return arrays as lists, not Python tuples.
        normalized["missing_gates"] = list(result.missing_gates)
        results.append(normalized)
    return {
        "schema_version": SCHEMA,
        "status": "SOURCE_ELIGIBILITY_AUDIT_ONLY",
        "candidate_count": len(results),
        "direct_structural_worldline_receipt_count": 0,
        "source_eligible_count": sum(
            item["status"] == "SOURCE_COMPARATOR_ELIGIBLE_FOR_WORLDLINE_TEST_NOT_BALANCE"
            for item in results
        ),
        "outcome_fitness_values_reconstructed": False,
        "independent_biological_clusters_added": 0,
        "results": results,
        "claim_ceiling": "source_evidence_only_no_matched_direct_structural_BALANCE",
    }
