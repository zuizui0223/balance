"""Core API for Chapter 2 BALANCE-domain analysis."""

from .boundary import (
    DEFAULT_BOUNDARY_TOLERANCE,
    TwoMarginPath,
    TwoMarginPoint,
    analyze_two_margin_path,
    classify_two_margin_point,
    positive_support_monotone,
)
from .static import BalancePathResult, BalancePathTopologyError, analyze_balance_path
from .dynamics import SwitchingCostResult, switching_cost_state
from .world import (
    BalanceDomainGeometry,
    MiddleWorldCertificate,
    balance_domain_geometry,
    classify_middle_world,
)
from .phase import NormalizedPhasePoint, normalized_phase_point
from .worldlines import WorldlineComparison, compare_worldlines
from .worldline_path import WorldlinePathResult, analyze_worldline_path
from .concordance import CriticalConcordanceResult, compare_critical_paths
from .definition_concordance import (
    CrossingBracket,
    DefinitionConcordance,
    analyze_definitions,
    compare_definition_brackets,
    crossing_bracket,
)
from .receipt import Interval, MiddleWorldReceipt, classify_bounded_receipt
from .handoff import ConflictHandoff, consume_conflict_handoff
from .pedicularis_xy import PedicularisXYBalanceReceipt, consume_pedicularis_xy_surface
from .depth_path import DeepestMiddleWorldPoint, deepest_middle_point
from .sensitivity import (
    BoundarySensitivity,
    DeepestPointSensitivity,
    boundary_sensitivity,
    deepest_point_sensitivity,
)
from .environmental_depth import EnvironmentalDepth, environmental_depth
from .metric_depth import (
    MetricBoundaryDepth,
    diagonal_metric_boundary_depth,
    metric_middle_world_depth,
)
from .metric_center import (
    ConstantSlopeCenters,
    constant_slope_centers,
    metric_middle_coordinate,
)
from .multi_alternative import (
    MultiAlternativeState,
    classify_multi_alternative_middle_world,
)
from .accessibility_scope import AccessibilityScopeBounds, accessibility_scope_bounds
from .covering_certificate import (
    CoveringCertificate,
    certified_balance_ball_radius,
    certified_outside_ball_radius,
    lipschitz_covering_certificate,
    lipschitz_lower_envelope,
    maximum_covering_radius_for_target_depth,
    multi_margin_lower_depth,
)
from .affine_envelope import (
    EndpointReserveCertificate,
    EnvelopeSegment,
    affine_upper_envelope_segments,
    alternative_reserve,
    endpoint_reserve_certificate,
    threat_switch_bound,
)
from .threat_stability import (
    ThreatStability,
    diagonal_affine_gradient_from_minimum_switch,
    diagonal_affine_threat_distance,
    lipschitz_threat_radius,
    threat_fragility_index,
)
from .concave_domain import (
    ConcaveSegmentCertificate,
    IntervalChordClassification,
    JensenAudit,
    StrongConcaveChordAudit,
    audit_concave_margin,
    audit_strong_concave_chord,
    certify_concave_balance_segment,
    classify_interval_concave_chord,
    concave_segment_lower_bounds,
    interval_concave_bulge_bounds,
    robust_positive_concave_endpoints,
    strong_concave_bulge_bounds,
)
from .width_depth import WidthDepthBounds, constant_slope_depth, width_depth_bounds
from .factorial_selection import (
    CONTRAST_ORDER,
    TREATMENT_ORDER,
    FactorialSelectionReceipt,
    analyze_factorial_agent_selection,
)
from .peucedanum_raw import (
    PLOT_ORDER,
    PUBLISHED_2025,
    RawInventory,
    ReproductionGate,
    published_regime_reproduction_gate,
    validate_normalized_rows,
)
from .longitudinal_mosaic import LongitudinalMosaicResult, classify_longitudinal_mosaic

__all__ = [
    "AccessibilityScopeBounds",
    "BalanceDomainGeometry",
    "BalancePathResult",
    "BalancePathTopologyError",
    "BoundarySensitivity",
    "CONTRAST_ORDER",
    "ConcaveSegmentCertificate",
    "ConflictHandoff",
    "ConstantSlopeCenters",
    "CoveringCertificate",
    "CriticalConcordanceResult",
    "CrossingBracket",
    "DEFAULT_BOUNDARY_TOLERANCE",
    "DeepestMiddleWorldPoint",
    "DeepestPointSensitivity",
    "DefinitionConcordance",
    "EndpointReserveCertificate",
    "EnvelopeSegment",
    "EnvironmentalDepth",
    "FactorialSelectionReceipt",
    "Interval",
    "IntervalChordClassification",
    "JensenAudit",
    "LongitudinalMosaicResult",
    "MetricBoundaryDepth",
    "MiddleWorldCertificate",
    "MiddleWorldReceipt",
    "MultiAlternativeState",
    "NormalizedPhasePoint",
    "PLOT_ORDER",
    "PUBLISHED_2025",
    "PedicularisXYBalanceReceipt",
    "RawInventory",
    "ReproductionGate",
    "StrongConcaveChordAudit",
    "SwitchingCostResult",
    "TREATMENT_ORDER",
    "ThreatStability",
    "TwoMarginPath",
    "TwoMarginPoint",
    "WidthDepthBounds",
    "WorldlineComparison",
    "WorldlinePathResult",
    "accessibility_scope_bounds",
    "affine_upper_envelope_segments",
    "alternative_reserve",
    "analyze_balance_path",
    "analyze_definitions",
    "analyze_factorial_agent_selection",
    "analyze_two_margin_path",
    "analyze_worldline_path",
    "audit_concave_margin",
    "audit_strong_concave_chord",
    "balance_domain_geometry",
    "boundary_sensitivity",
    "certified_balance_ball_radius",
    "certified_outside_ball_radius",
    "certify_concave_balance_segment",
    "classify_bounded_receipt",
    "classify_interval_concave_chord",
    "classify_longitudinal_mosaic",
    "classify_middle_world",
    "classify_multi_alternative_middle_world",
    "classify_two_margin_point",
    "compare_critical_paths",
    "compare_definition_brackets",
    "compare_worldlines",
    "concave_segment_lower_bounds",
    "constant_slope_centers",
    "constant_slope_depth",
    "consume_conflict_handoff",
    "consume_pedicularis_xy_surface",
    "crossing_bracket",
    "deepest_middle_point",
    "deepest_point_sensitivity",
    "diagonal_affine_gradient_from_minimum_switch",
    "diagonal_affine_threat_distance",
    "diagonal_metric_boundary_depth",
    "endpoint_reserve_certificate",
    "environmental_depth",
    "interval_concave_bulge_bounds",
    "lipschitz_covering_certificate",
    "lipschitz_lower_envelope",
    "lipschitz_threat_radius",
    "maximum_covering_radius_for_target_depth",
    "metric_middle_coordinate",
    "metric_middle_world_depth",
    "multi_margin_lower_depth",
    "normalized_phase_point",
    "positive_support_monotone",
    "published_regime_reproduction_gate",
    "robust_positive_concave_endpoints",
    "strong_concave_bulge_bounds",
    "switching_cost_state",
    "threat_fragility_index",
    "threat_switch_bound",
    "validate_normalized_rows",
    "width_depth_bounds",
]
