"""Prospective, falsifiable pollen-supply versus visitation-opportunity models.

Neither function fits data or identifies an evolutionary architecture.
The first is a two-gate *hypothesis* for pollen delivery and a saturating
female-output proxy. The second tracks donor-pollen mass through controlled
visitor arrival sequences and a fixed first-event delayed pollen release.
All numbers in the CLI are synthetic illustrations, NOT observed effects.
"""
from __future__ import annotations

from math import expm1, isfinite


def _nonnegative(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite nonnegative number")
    v = float(value)
    if not isfinite(v) or v < 0:
        raise ValueError(f"{name} must be a finite nonnegative number")
    return v


def _fraction(name: str, value: float) -> float:
    v = _nonnegative(name, value)
    if v > 1:
        raise ValueError(f"{name} must be between 0 and 1")
    return v


def service_gated_output(
    *,
    initial_source_pollen: float,
    source_removal_fraction: float,
    legitimate_visits: int,
    pickup_capacity_per_visit: float,
    transfer_success_fraction: float,
    response_scale: float,
    output_ceiling: float,
    hand_deposited_pollen: float = 0,
) -> dict[str, float | int]:
    """Two independently testable constraints: source stock and visit capacity.

    Mechanistic hypotheses, not identities of a biological population:
      effective_delivery = eta * min[(1-r)P, n*c] + H;
      output_proxy = Ymax * (1-exp(-effective_delivery/kappa)).
    H is pollen *directly applied to recipients*, so it bypasses both
    source-stock and insect-service gates. The saturation map is an explicit
    phenomenological assumption, not a measured seed or paternal output.
    """
    p = _nonnegative("initial_source_pollen", initial_source_pollen)
    r = _fraction("source_removal_fraction", source_removal_fraction)
    if isinstance(legitimate_visits, bool) or not isinstance(legitimate_visits, int) or legitimate_visits < 0:
        raise ValueError("legitimate_visits must be an integer >= 0")
    c = _nonnegative("pickup_capacity_per_visit", pickup_capacity_per_visit)
    eta = _fraction("transfer_success_fraction", transfer_success_fraction)
    k = _nonnegative("response_scale", response_scale)
    if k == 0:
        raise ValueError("response_scale must be positive")
    ymax = _nonnegative("output_ceiling", output_ceiling)
    hand = _nonnegative("hand_deposited_pollen", hand_deposited_pollen)
    stock = p * (1.0 - r)
    capacity = legitimate_visits * c
    export_proxy = min(stock, capacity)
    delivered = eta * export_proxy + hand
    output = ymax * (-expm1(-delivered / k))
    if not all(isfinite(z) for z in (stock, capacity, delivered, output)):
        raise ValueError("Non-finite scenario result")
    return {
        "source_pollen_after_reduction": stock,
        "visit_pickup_capacity": capacity,
        "legitimate_visit_count": legitimate_visits,
        "donor_export_proxy": export_proxy,
        "effective_recipient_delivery_proxy": delivered,
        "bounded_female_output_proxy": output,
    }


def simulate_visitor_order(
    *,
    event_order: str,
    initial_pollen_total: float,
    delayed_release_fraction: float,
    legitimate_removal_fraction: float,
    thief_removal_fraction: float,
    effective_transfer_fraction: float = 1,
) -> dict:
    """Closed source-pollen inventory, with two L and one T visit.

    Pollen is released once at t=0 and optionally a second time just AFTER
    the first visitor; all release schedules present the same total pollen.
    L removes alpha of current stock, but only eta of this removed pollen
    contributes to the donor-export *proxy*. T removes beta without service.
    No pollen growth, behavioral response, pollen viability change, recipient
    competition, or genetic paternity is included.
    """
    if not isinstance(event_order, str) or len(event_order) != 3 or sorted(event_order) != ["L", "L", "T"]:
        raise ValueError("event_order must contain exactly two L and one T")
    P = _nonnegative("initial_pollen_total", initial_pollen_total)
    late = _fraction("delayed_release_fraction", delayed_release_fraction)
    alpha = _fraction("legitimate_removal_fraction", legitimate_removal_fraction)
    beta = _fraction("thief_removal_fraction", thief_removal_fraction)
    eta = _fraction("effective_transfer_fraction", effective_transfer_fraction)
    stock = P * (1-late)
    legitimate_removed = 0.0
    stolen = 0.0
    transported = 0.0
    history = []
    for i, event in enumerate(event_order):
        before = stock
        pickup = 0.0
        theft = 0.0
        if event == "L":
            pickup = alpha * stock
            legitimate_removed += pickup
            transported += eta * pickup
            stock -= pickup
        else:
            theft = beta * stock
            stolen += theft
            stock -= theft
        new_release = P * late if i == 0 else 0.0
        stock += new_release
        history.append({
            "visit_index": i + 1,
            "visitor_role": event,
            "available_pollen_before": before,
            "legitimate_pollen_removed": pickup,
            "pollen_stolen": theft,
            "pollen_released_after": new_release,
            "available_pollen_after": stock,
        })
    mass_residual = P - (stock + legitimate_removed + stolen)
    if abs(mass_residual) > 1e-9 * max(1, P):
        raise ValueError("Closed pollen inventory is not conserved")
    return {
        "schedule": event_order,
        "pollen_total": P,
        "delayed_fraction": late,
        "total_legitimate_pollen_removed": legitimate_removed,
        "total_pollen_stolen": stolen,
        "effective_export_proxy": transported,
        "remaining_pollen": stock,
        "conservation_residual": mass_residual,
        "visitor_trace": history,
    }


def build_synthetic_gate_and_order_scenarios() -> dict:
    """Frozen illustrative choices, not calibrated to Clusia or Polemonium."""
    source_pollen = 100.0
    stolen_fraction = 0.5
    visit_capacity = 10.0
    common = dict(
        initial_source_pollen=source_pollen,
        pickup_capacity_per_visit=visit_capacity,
        transfer_success_fraction=1.0,
        response_scale=50.0,
        output_ceiling=10.0,
    )
    supply = {}
    for visits in (2, 7):
        base = service_gated_output(
            **common, source_removal_fraction=0.0,
            legitimate_visits=visits,
        )
        removal = service_gated_output(
            **common, source_removal_fraction=stolen_fraction,
            legitimate_visits=visits,
        )
        supplement = service_gated_output(
            **common, source_removal_fraction=0.0,
            legitimate_visits=visits, hand_deposited_pollen=20.0,
        )
        supply[str(visits)] = {
            "baseline": base,
            "source_reduced": removal,
            "hand_supplemented": supplement,
            "source_reduction_effect_on_output_proxy": (
                base["bounded_female_output_proxy"]
                - removal["bounded_female_output_proxy"]
            ),
            "direct_hand_supplementation_gain": (
                supplement["bounded_female_output_proxy"]
                - base["bounded_female_output_proxy"]
            ),
        }

    order = {}
    for arrival in ("TLL", "LTL"):
        arms = {}
        for thief, label in ((0.0, "sham_no_theft"), (0.5, "real_theft")):
            for delayed, programme in ((0.0, "burst"), (0.5, "delayed_half")):
                arms[f"{label}__{programme}"] = simulate_visitor_order(
                    event_order=arrival,
                    initial_pollen_total=source_pollen,
                    delayed_release_fraction=delayed,
                    legitimate_removal_fraction=0.3,
                    thief_removal_fraction=thief,
                    effective_transfer_fraction=1.0,
                )
        def stage_advantage(condition: str) -> float:
            return (
                arms[f"{condition}__delayed_half"]["effective_export_proxy"]
                - arms[f"{condition}__burst"]["effective_export_proxy"]
            )
        order[arrival] = {
            "arms": arms,
            "delayed_minus_burst_under_theft": stage_advantage("real_theft"),
            "delayed_minus_burst_under_sham": stage_advantage("sham_no_theft"),
            "thief_specific_difference_in_stage_advantage": (
                stage_advantage("real_theft") - stage_advantage("sham_no_theft")
            ),
        }
    triple_difference = (
        order["TLL"]["thief_specific_difference_in_stage_advantage"]
        - order["LTL"]["thief_specific_difference_in_stage_advantage"]
    )
    return {
        "analysis": "BALANCE_POLLEN_SUPPLY_OPPORTUNITY_GATES_V1",
        "status": "SYNTHETIC_PROSPECTIVE_MODEL_ONLY",
        "fixed_synthetic_parameters": {
            "source_pollen": source_pollen,
            "source_removed_fraction": stolen_fraction,
            "legitimate_visit_pollen_pickup_capacity": visit_capacity,
            "recipient_response_scale": 50,
            "response_proxy_ceiling": 10,
            "delayed_release_fraction": 0.5,
            "legitimate_fractional_pickup_per_visit": 0.3,
            "hand_added_recipient_pollen": 20,
        },
        "supply_by_visits": supply,
        "visitor_sequence": order,
        "thief_specific_three_way_interaction_proxy": triple_difference,
        "data_used_for_model_calibration": False,
        "empirical_fitness_or_paternity_inferred": False,
        "architecture_fitness_comparison_performed": False,
    }


def build_closed_stock_parameter_sweep() -> dict:
    """Grid sensitivity within this *one* assumed fractional-removal mechanism.

    This is an exhaustive fixed 3x3x3x3 illustration, not a fitted parameter
    posterior or external biological replication. All 81 combinations share
    the same donor-stock and no-behavior-feedback assumptions.
    """
    alpha_grid = (0.1, 0.3, 0.6)
    beta_grid = (0.2, 0.5, 0.8)
    late_grid = (0.25, 0.5, 0.75)
    eta_grid = (0.25, 0.5, 1.0)
    total = 0
    early_protected = 0
    early_opportunity_cost = 0
    triple_positive = 0
    gammas: list[float] = []
    for alpha in alpha_grid:
        for beta in beta_grid:
            for late in late_grid:
                for eta in eta_grid:
                    def relative_release_advantage(order: str, thief: float) -> float:
                        common = {
                            "event_order": order,
                            "initial_pollen_total": 100.0,
                            "legitimate_removal_fraction": alpha,
                            "thief_removal_fraction": thief,
                            "effective_transfer_fraction": eta,
                        }
                        staged = simulate_visitor_order(
                            **common, delayed_release_fraction=late
                        )["effective_export_proxy"]
                        burst = simulate_visitor_order(
                            **common, delayed_release_fraction=0.0
                        )["effective_export_proxy"]
                        return staged - burst

                    tll = relative_release_advantage("TLL", beta)
                    ltl = relative_release_advantage("LTL", beta)
                    gamma = (
                        tll - relative_release_advantage("TLL", 0.0)
                        - ltl + relative_release_advantage("LTL", 0.0)
                    )
                    total += 1
                    early_protected += int(tll > 1e-10)
                    early_opportunity_cost += int(ltl < -1e-10)
                    triple_positive += int(gamma > 1e-10)
                    gammas.append(gamma)
    if total != 81:
        raise ValueError("Fixed scenario-grid cardinality changed")
    return {
        "status": "ALL_SYNTHETIC_SAME_CLOSED_STOCK_MECHANISM",
        "model_grid_axes": {
            "legitimate_fraction": list(alpha_grid),
            "theft_fraction": list(beta_grid),
            "delayed_release_fraction": list(late_grid),
            "effective_transfer_fraction": list(eta_grid),
        },
        "parameter_combinations": total,
        "positive_delayed_advantage_if_thief_first": early_protected,
        "negative_delayed_advantage_if_legitimate_first": early_opportunity_cost,
        "positive_thief_adjusted_triple_contrast": triple_positive,
        "minimum_thief_adjusted_triple_contrast": min(gammas),
        "maximum_thief_adjusted_triple_contrast": max(gammas),
        "empirical_studies_counted": 0,
        "inference_limit": "model-internal robustness only, no independent field validation",
    }
