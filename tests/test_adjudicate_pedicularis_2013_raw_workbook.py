"""No fake field evidence: algebraic tests for exact-source ANOVA reproducer."""
import pytest
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

_SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "adjudicate_pedicularis_2013_raw_workbook.py"
_SPEC = spec_from_file_location("pedicularis_2013_source_anova", _SOURCE)
_mod = module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(_mod)
SOURCE_SHA256 = _mod.SOURCE_SHA256
PUBLISHED_F = _mod.PUBLISHED_F
anova_two_factor = _mod.anova_two_factor
_source_rows = _mod._source_rows
EXPECTED_COUNTS_FRUIT = _mod.EXPECTED_COUNTS_FRUIT
EXPECTED_FRUIT_HEADER = _mod.EXPECTED_FRUIT_HEADER


def test_independent_balanced_two_factor_oracle():
    # For each of the four cells, symmetric residuals +/-1 give RSS=8,
    # df=4 and MSE=2; orthogonal contrasts have X'X diagonal=8.
    # Coefficients: factor=3, density=2, interaction=1 => F=36,16,4.
    rows = []
    for year in (1, 2):
        for density in (1, 2):
            a = 2*year-3
            b = 2*density-3
            for error in (-1, 1):
                rows.append([year,density,1,
                             20+3*a+2*b+a*b+error,1,0])
    result = anova_two_factor(rows,3,0)
    assert result["n"] == 8
    assert result["df_residual"] == 4
    assert result["factor"] == pytest.approx(36)
    assert result["density"] == pytest.approx(16)
    assert result["interaction"] == pytest.approx(4)
    assert result["patch_cluster_robust"] is False


def test_zero_residual_uncertainty_not_promoted():
    r = []
    for year in (1,2):
        for den in (1,2):
            for i in (0,1):
                r.append([year,den,1,3.0,0,0])
    with pytest.raises(ValueError, match="degenerate outcome"):
        anova_two_factor(r,3,0)


def test_known_published_seed_model_support_is_not_claimed_cluster_robust():
    assert SOURCE_SHA256 == (
        "d1dab0ea6f4371370aacd13106eee57017abbccccb3cd12dea75b69bdfa60380"
    )
    assert len(PUBLISHED_F) == 8
    assert sum(len([f for f in ("factor","density","interaction") if f in item])
               for item in PUBLISHED_F.values()) == 24
    assert all(x["n"] - 4 == x["df_residual"]
               for x in PUBLISHED_F.values())


def test_source_rows_validate_exact_category_and_legend():
    records = []
    for key,n in EXPECTED_COUNTS_FRUIT.items():
        year,den,size = key.split("_")
        yr = 1 if year=="2005" else 2
        d = 1 if den=="sparse" else 2
        si = 1 if size=="small" else 2
        records.extend([[yr,d,si,10,20,30] for _ in range(n)])
    legends = [
        ["1=2005","1=sparse","1=small",None,None,None],
        ["2=2011","2=dense","2=large",None,None,None],
    ]
    rows, counts = _source_rows(EXPECTED_FRUIT_HEADER,
                                records+legends,
                                EXPECTED_FRUIT_HEADER,
                                EXPECTED_COUNTS_FRUIT)
    assert len(rows)==74
    assert counts["2011_dense_large"]==25
    with pytest.raises(ValueError,match="source worksheet"):
        _source_rows(EXPECTED_FRUIT_HEADER,records,
                     EXPECTED_FRUIT_HEADER,EXPECTED_COUNTS_FRUIT)


def test_frozen_real_source_concordance_keeps_independent_patch_gate_closed():
    import json
    from pathlib import Path
    target = (Path(__file__).resolve().parents[1] /
              "data/PEDICULARIS_2013_SOURCE_SEED_ANOVA_CONCORDANCE_V1.json")
    data = json.loads(target.read_text(encoding="utf-8"))
    assert data["source_sha256"] == SOURCE_SHA256
    assert data["source_has_patch_id"] is False
    assert data["source_has_plant_id"] is False
    assert data["patch_clustered_inference_identifiable"] is False
    assert data["causal_density_identified"] is False
    assert data["published_F_matches_to_3_decimals"] == 18
    assert data["fruit_biological_rows"] == 74
    assert data["seed_biological_rows"] == 2930
    assert data["missing_initial_seed_rows"] == 328
    for name,model in data["replicated_seed_models"].items():
        target_f = PUBLISHED_F[name]
        assert model["n"] == target_f["n"]
        assert model["residual_df"] == target_f["df_residual"]
        for key in ("density","interaction"):
            assert abs(model["F_"+key] - target_f[key]) < 0.00055
        alt = "F_size" if name.startswith("Table2") else "F_year"
        assert abs(model[alt] - target_f["factor"]) < 0.00055



def test_missing_initial_seed_bounds_do_not_impute_complete_predation():
    initial_seed_missingness_bounds = _mod.initial_seed_missingness_bounds
    rows=[]
    for year in (1,2):
        for density in (1,2):
            rows.append([year,density,2,20.0,16.0,20.0])
            rows.append([year,density,2,None,0.0,100.0])
    result=initial_seed_missingness_bounds(rows)
    assert result["status"]=="INITIAL_SEED_RATE_OUTCOME_DEPENDENT_MISSINGNESS_HOLD"
    s=result["groups"]["2011"]["by_density"]["sparse"]
    assert s["n_initial_missing"]==1
    assert s["observed_initial_mean_percent"]==pytest.approx(20.0)
    assert s["population_mean_identification_lower_percent"]==pytest.approx(10.0)
    assert s["population_mean_identification_upper_percent"]==pytest.approx(60.0)
    assert result["groups"]["2011"][
        "dense_minus_sparse_initial_mean_identified_interval_percent_points"
    ] == pytest.approx([-50.0,50.0])
    assert result["causal_pollination_or_fertilization_effect_identified"] is False


def test_missing_initial_with_nonmaximal_predation_is_source_drift():
    initial_seed_missingness_bounds = _mod.initial_seed_missingness_bounds
    rows=[]
    for year in (1,2):
        for density in (1,2):
            rows.append([year,density,2,None,0.0,99.0])
    with pytest.raises(ValueError,match="predation=100"):
        initial_seed_missingness_bounds(rows)


def test_table2_fruit_extension_is_not_a_patch_density_claim():
    # The article's Table 2 fruit-model ANOVAs use 2011 spikes (n=58)
    # not the 2,349 seed-sheet records. Only unclustered F are reproduced.
    for outcome, expected in (
        ("Table2_fruit_set", (0.206, 2.368, 3.060)),
        ("Table2_fruit_predation", (4.573, 26.314, 10.605)),
    ):
        model = PUBLISHED_F[outcome]
        assert (model["n"], model["df_residual"]) == (58, 54)
        assert (model["factor"], model["density"], model["interaction"]) == expected

    import json
    from pathlib import Path
    receipt = json.loads((
        Path(__file__).resolve().parents[1]
        / "data/PEDICULARIS_2013_ANOVA_24F_SOURCE_RECEIPT_V1.json"
    ).read_text(encoding="utf-8"))
    assert receipt["source"]["workbook_sha256"] == SOURCE_SHA256
    assert receipt["published_F_tests_matched"] == 24
    assert len(receipt["model_records"]) == 8
    assert receipt["sheet_support"]["patch_id_present"] is False
    assert receipt["missing_claims"]["patch_clustered_standard_errors_computed"] is False
    assert receipt["missing_claims"]["component_Allee_effect_invalidated"] is False
    assert receipt["missing_claims"]["sparse_patch_water_defence_intervention_present"] is False
    for item in receipt["model_records"]:
        paper = PUBLISHED_F[item["model"]]
        assert item["n"] == paper["n"]
        assert item["residual_df"] == paper["df_residual"]
        for name, factor_key in (
            ("density", "density"), ("interaction", "interaction"),
            ("year" if item["model"].startswith("Table1") else "size", "factor"),
        ):
            assert abs(item["reproduced_F"][name] - paper[factor_key]) < 0.00055
            assert item["published_F"][name] == paper[factor_key]
