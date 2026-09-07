from balance_domain.envelope_equivalence import (
    active_threats_at_context,
    compare_sampled_envelopes,
    identify_threats_with_auxiliary,
    sampled_balance_state,
    sampled_reserve,
    upper_envelope,
)


def test_different_registries_can_have_the_same_sampled_envelope():
    registry_a = {
        "D1": [1.0, 2.0, 1.5],
        "D2": [0.5, 1.0, 2.0],
    }
    # D3 is different biologically but never pierces the existing envelope.
    registry_b = {
        **registry_a,
        "D3": [0.2, 1.8, 1.9],
    }

    comparison = compare_sampled_envelopes(registry_a, registry_b)
    assert comparison.equivalent
    assert comparison.max_abs_gap == 0.0


def test_envelope_equivalence_implies_same_reserve_and_balance_state():
    registry_a = {
        "D1": [1.0, 2.0, 1.5],
        "D2": [0.5, 1.0, 2.0],
    }
    registry_b = {
        "X": [1.0, 2.0, 2.0],
        "Y": [0.4, 1.2, 1.8],
    }
    shared = [2.5, 2.5, 2.5]
    conflict = [0.3, 0.4, 0.5]

    env_a = upper_envelope(registry_a)
    env_b = upper_envelope(registry_b)
    assert env_a == env_b

    rho_a = sampled_reserve(shared, env_a)
    rho_b = sampled_reserve(shared, env_b)
    assert rho_a == rho_b
    assert sampled_balance_state(conflict, rho_a) == sampled_balance_state(conflict, rho_b)


def test_state_equivalence_is_weaker_than_envelope_equivalence():
    shared = [3.0, 3.0]
    conflict = [0.2, 0.2]
    registry_a = {"D1": [1.0, 1.0]}
    registry_b = {"D2": [2.0, 2.0]}

    env_a = upper_envelope(registry_a)
    env_b = upper_envelope(registry_b)
    assert env_a != env_b

    rho_a = sampled_reserve(shared, env_a)
    rho_b = sampled_reserve(shared, env_b)
    assert sampled_balance_state(conflict, rho_a) == (True, True)
    assert sampled_balance_state(conflict, rho_b) == (True, True)
    assert rho_a != rho_b


def test_envelope_piercing_scope_expansion_changes_predictions():
    base = {"D1": [1.0, 1.0]}
    expanded = {**base, "D_new": [1.5, 3.2]}

    comparison = compare_sampled_envelopes(base, expanded)
    assert not comparison.equivalent
    assert comparison.envelope_a == (1.0, 1.0)
    assert comparison.envelope_b == (1.5, 3.2)


def test_tied_envelope_identifies_active_threat_set_not_unique_label():
    registry = {
        "D1": [1.0, 2.0],
        "D2": [1.0, 2.0],
        "D3": [0.5, 1.0],
    }
    assert active_threats_at_context(registry, 0) == ("D1", "D2")
    assert active_threats_at_context(registry, 1) == ("D1", "D2")


def test_injective_auxiliary_code_breaks_an_envelope_tie():
    active = ("D1", "D2")
    codes = {"D1": "retained", "D2": "drained"}
    assert identify_threats_with_auxiliary(active, codes, "retained") == ("D1",)


def test_noninjective_auxiliary_code_preserves_partial_identification():
    active = ("D1", "D2", "D3")
    codes = {"D1": "retained", "D2": "retained", "D3": "drained"}
    assert identify_threats_with_auxiliary(active, codes, "retained") == ("D1", "D2")
