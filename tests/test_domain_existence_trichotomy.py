from balance_domain.domain_existence import classify_domain_path


def test_no_positive_width_balance_when_worldline_is_already_nonnegative():
    result = classify_domain_path([0.0, 0.2, 0.5], [0.0, 0.1, 0.3])
    assert result.classification == "NO_OBSERVED_POSITIVE_WIDTH_BALANCE"


def test_finite_balance_domain_when_first_crossing_occurs_after_conflict_onset():
    result = classify_domain_path([0.0, 0.1, 0.3, 0.5], [-0.2, -0.1, 0.0, 0.2])
    assert result.classification == "FINITE_BALANCE_DOMAIN_OBSERVED_ON_SAMPLED_PATH"
    assert result.delta_nondecreasing is True


def test_persistent_balance_when_no_crossing_is_observed():
    result = classify_domain_path([0.0, 0.1, 0.3, 0.5], [-0.5, -0.4, -0.2, -0.1])
    assert result.classification == "PERSISTENT_BALANCE_OVER_OBSERVED_PATH"


def test_nonmonotone_path_is_not_forced_into_the_monotone_trichotomy():
    result = classify_domain_path([0.0, 0.2, 0.4, 0.6], [-0.3, -0.1, 0.2, -0.2])
    assert result.classification == "NONMONOTONE_PATH_REQUIRES_REENTRY_AUDIT"
