import pytest

from balance_domain.bounded_switching_design import identify_bounded_switching


UP = [("0.095", "0.105", "shared"), ("0.115", "0.125", "differentiated")]
DOWN = [("-0.055", "-0.045", "differentiated"), ("-0.085", "-0.075", "shared")]


def _identify(**overrides):
    kwargs = dict(
        common_phi_scale="matched payoff scale",
        fixed_context="same environment",
        latent_monotone_and_instantaneous_declared=True,
    )
    kwargs.update(overrides)
    return identify_bounded_switching(UP, DOWN, **kwargs)


def test_receipt_freezes_normalized_scale_and_context():
    result = _identify(
        common_phi_scale="  matched payoff scale  ",
        fixed_context=" same environment ",
    )
    assert result.common_phi_scale == "matched payoff scale"
    assert result.fixed_context == "same environment"


@pytest.mark.parametrize("field", ["common_phi_scale", "fixed_context"])
@pytest.mark.parametrize("bad", [None, "", "None", "null", "nan", "REQUIRED_BEFORE_USE"])
def test_missing_or_placeholder_provenance_fails_closed(field, bad):
    with pytest.raises(ValueError, match=f"{field}.*frozen"):
        _identify(**{field: bad})


def test_monotone_instantaneous_declaration_remains_literal_true_gate():
    for bad in (False, None, 1, "true"):
        with pytest.raises(ValueError, match="latent monotone instantaneous rule"):
            _identify(latent_monotone_and_instantaneous_declared=bad)
