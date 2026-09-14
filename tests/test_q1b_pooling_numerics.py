import json
import math
from pathlib import Path

import pytest

from balance_domain.q1b_pooling import dl_mkh

ROOT = Path(__file__).resolve().parents[1]
FRAGARIA = ROOT / "data" / "BALANCE_FRAGARIA_Q1B_RECEIPT_V1.json"
IMPATIENS = ROOT / "data" / "BALANCE_IMPATIENS_Q1B_CLUSTER_AGGREGATE_V1.json"
GYMNADENIA = ROOT / "data" / "BALANCE_GYMNADENIA_Q1B_RECEIPT_V1.json"
FROZEN_POOL = ROOT / "data" / "BALANCE_Q1B_FIRST_POOL_V1.json"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_exact_pooling_reproduces_frozen_first_pool():
    frag = _load(FRAGARIA)
    imp = _load(IMPATIENS)
    gym = _load(GYMNADENIA)
    frozen = _load(FROZEN_POOL)
    studies = (frag, imp, gym)

    for j, name in enumerate(frag["contrast_order"]):
        yi = [study["mediated_contrasts"][j] for study in studies]
        vi = [study["contrast_covariance"][j][j] for study in studies]
        observed = dl_mkh(yi, vi)
        expected = frozen["pooled"][name]
        for key in (
            "mu_random",
            "se_mkh",
            "tau2_DL",
            "Q_fixed",
            "I2_percent",
            "mu_fixed",
        ):
            assert observed[key] == pytest.approx(expected[key], rel=1e-12, abs=1e-15)
        assert observed["ci95_mkh"] == pytest.approx(
            expected["ci95_mkh"], rel=1e-12, abs=1e-15
        )
        assert observed["k"] == expected["k"] == 3


def test_subnormal_positive_variance_does_not_create_infinite_weight():
    result = dl_mkh(
        (1.0, 2.0, 3.0),
        (5.0e-324, 1.0e-300, 1.0e-300),
    )
    assert result["k"] == 3
    assert result["mu_fixed"] == pytest.approx(1.0)
    for key in (
        "mu_random",
        "se_mkh",
        "tau2_DL",
        "Q_fixed",
        "I2_percent",
        "mu_fixed",
    ):
        assert math.isfinite(result[key])
    assert all(math.isfinite(value) for value in result["ci95_mkh"])


def test_first_pool_helper_rejects_wrong_k_and_nonpositive_variance():
    with pytest.raises(ValueError, match="exactly k=3"):
        dl_mkh((0.1, 0.2), (0.01, 0.02))
    with pytest.raises(ValueError, match="strictly positive"):
        dl_mkh((0.1, 0.2, 0.3), (0.01, 0.0, 0.03))
    with pytest.raises(ValueError, match="strictly positive"):
        dl_mkh((0.1, 0.2, 0.3), (0.01, -0.02, 0.03))


def test_pooling_rejects_nonfinite_inputs():
    with pytest.raises(ValueError, match="finite"):
        dl_mkh((0.1, math.nan, 0.3), (0.01, 0.02, 0.03))
    with pytest.raises(ValueError, match="finite"):
        dl_mkh((0.1, 0.2, 0.3), (0.01, math.inf, 0.03))
