"""Core API for Chapter 2 BALANCE-domain analysis."""

from .static import BalancePathResult, analyze_balance_path
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
from .width_depth import WidthDepthBounds, constant_slope_depth, width_depth_bounds
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
    "BalanceDomainGeometry",
    "BalancePathResult",
    "BoundarySensitivity",
    "ConflictHandoff",
    "ConstantSlopeCenters",
    "CriticalConcordanceResult",
    "CrossingBracket",
    "DeepestMiddleWorldPoint",
    "DeepestPointSensitivity",
    "DefinitionConcordance",
    "EnvironmentalDepth",
    "Interval",
    "LongitudinalMosaicResult",
    "MetricBoundaryDepth",
    "MiddleWorldCertificate",
    "MiddleWorldReceipt",
    "MultiAlternativeState",
    "NormalizedPhasePoint",
    "PLOT_ORDER",
    "PUBLISHED_2025",
    "RawInventory",
    "ReproductionGate",
    "SwitchingCostResult",
    "WidthDepthBounds",
    "WorldlineComparison",
    "WorldlinePathResult",
    "analyze_balance_path",
    "analyze_definitions",
    "analyze_worldline_path",
    "balance_domain_geometry",
    "boundary_sensitivity",
    "classify_bounded_receipt",
    "classify_longitudinal_mosaic",
    "classify_middle_world",
    "classify_multi_alternative_middle_world",
    "compare_critical_paths",
    "compare_definition_brackets",
    "compare_worldlines",
    "constant_slope_centers",
    "constant_slope_depth",
    "consume_conflict_handoff",
    "crossing_bracket",
    "deepest_middle_point",
    "deepest_point_sensitivity",
    "diagonal_metric_boundary_depth",
    "environmental_depth",
    "metric_middle_coordinate",
    "metric_middle_world_depth",
    "normalized_phase_point",
    "published_regime_reproduction_gate",
    "switching_cost_state",
    "validate_normalized_rows",
    "width_depth_bounds",
]
