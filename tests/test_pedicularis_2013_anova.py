"""Synthetic-only tests for exact published-F replay; no invented patch IDs."""
import math

import pytest

from balance_domain.pedicularis_2013_anova import (
    PUBLISHED, WORKBOOK_SHA256, audit, effect_ols_F, inverse,
)


def test_orthogonal_balanced_factor_density_with_exact_known_F():
    # y = 10 + 2*factor + 1*density + 3*factor*density + noise.
    # In each of 4 cells, residuals are +/-1: SSE=8, df=4, MSE=2.
    # Every slope variance MSE/8=.25 => factor F16, density F4,
    # interaction F36, independent of external statistics libraries.
    recs = []
    for f in (1,2):
        for d in (1,2):
            fac, dens = 2*f-3,2*d-3
            for noise in (-1,1):
                y = 10 + 2*fac + 1*dens + 3*fac*dens + noise
                recs.append([2,d,f,None,y,None])
    result = effect_ols_F(recs,4,2)
    assert result["n"] == 8
    assert result["residual_df"] == 4
    assert result["F"] == pytest.approx({
        "factor": 16, "density": 4, "interaction": 36,
    }, abs=1e-12)


def test_rank_deficient_or_biological_invalid_response_fails_closed():
    with pytest.raises(ValueError, match="rank-deficient"):
        inverse([[1,1],[1,1]])
    with pytest.raises(ValueError, match="too few"):
        effect_ols_F([[2,1,1,None,2,10]]*4,4,2)
    bad = [[2,d,f,None,float(10 + d*f + i),None]
           for f in (1,2) for d in (1,2) for i in range(2)]
    bad[0][4] = float("nan")
    with pytest.raises(ValueError, match="nonfinite"):
        effect_ols_F(bad,4,2)
    bad[0][4] = float(10)
    bad[1][1] = "dense"
    with pytest.raises(ValueError, match="density/factor"):
        effect_ols_F(bad,4,2)


def test_predeclared_reproduction_ceiling_includes_fruit_2011():
    assert WORKBOOK_SHA256 == (
        "d1dab0ea6f4371370aacd13106eee57017abbccccb3cd12dea75b69bdfa60380"
    )
    assert len(PUBLISHED) == 8
    assert sum(len(v)-2 for v in PUBLISHED.values()) == 24
    assert PUBLISHED["Table2_fruit_set"]["density"] == 2.368
    assert PUBLISHED["Table2_fruit_predation"]["interaction"] == 10.605
    assert PUBLISHED["Table1_seed_predation"]["density"] == 166.220
    assert PUBLISHED["Table2_seed_predation"]["interaction"] == 106.270
