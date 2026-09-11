import csv
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
POINTS = ROOT / "data" / "BALANCE_Q1B_FIGURE2_POINTS_V1.csv"
POOL = ROOT / "data" / "BALANCE_Q1B_FIRST_POOL_V1.json"
FRAGARIA = ROOT / "data" / "BALANCE_FRAGARIA_Q1B_RECEIPT_V1.json"
GYMNADENIA = ROOT / "data" / "BALANCE_GYMNADENIA_Q1B_RECEIPT_V1.json"
IMPATIENS_AGG = ROOT / "data" / "BALANCE_IMPATIENS_Q1B_CLUSTER_AGGREGATE_V1.json"


def _rows():
    with POINTS.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_figure2_has_three_study_points_and_one_pool_per_contrast():
    rows = _rows()
    assert len(rows) == 16
    contrasts = sorted({r["contrast"] for r in rows})
    assert len(contrasts) == 4
    for contrast in contrasts:
        subset = [r for r in rows if r["contrast"] == contrast]
        assert {r["cluster"] for r in subset} == {"Fragaria", "Impatiens", "Gymnadenia", "Q1B pooled"}
        assert sum(r["entry_type"] == "study" for r in subset) == 3
        assert sum(r["entry_type"] == "pooled" for r in subset) == 1


def test_pooled_rows_match_frozen_first_pool():
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    rows = {(r["contrast"], r["cluster"]): r for r in _rows()}
    for contrast in pool["contrast_order"]:
        r = rows[(contrast, "Q1B pooled")]
        p = pool["pooled"][contrast]
        assert float(r["estimate"]) == pytest.approx(p["mu_random"])
        assert float(r["ci_low"]) == pytest.approx(p["ci95_mkh"][0])
        assert float(r["ci_high"]) == pytest.approx(p["ci95_mkh"][1])


def test_study_points_match_frozen_receipts_without_inflating_impatiens_traits():
    frag = json.loads(FRAGARIA.read_text(encoding="utf-8"))
    gym = json.loads(GYMNADENIA.read_text(encoding="utf-8"))
    imp = json.loads(IMPATIENS_AGG.read_text(encoding="utf-8"))
    rows = {(r["contrast"], r["cluster"]): r for r in _rows()}

    for i, contrast in enumerate(frag["contrast_order"]):
        assert float(rows[(contrast, "Fragaria")]["estimate"]) == pytest.approx(frag["mediated_contrasts"][i])
        assert float(rows[(contrast, "Gymnadenia")]["estimate"]) == pytest.approx(gym["mediated_contrasts"][i])
        assert float(rows[(contrast, "Impatiens")]["estimate"]) == pytest.approx(imp["mediated_contrasts"][i])
        assert rows[(contrast, "Impatiens")]["independent_unit"] == "biological_cluster"

    assert imp["aggregation_rule"] == "equal_weight_mean_across_all_predeclared_traits"
    assert len(imp["traits"]) == 2


def test_figure2_labels_pool_as_conditional_and_keeps_negative_controls_outside_positive_points():
    from importlib.util import module_from_spec, spec_from_file_location

    script = ROOT / "scripts" / "build_balance_q1b_figure2.py"
    spec = spec_from_file_location("balance_q1b_fig2", script)
    mod = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    svg = mod.build_svg()
    assert "conditional summary of three positive-admitted clusters" in svg
    assert "not a general-effect meta-analysis" in svg
    assert "conditional summary" in svg
    assert "Specificity controls kept outside the strict positive-admitted Q1B summary" in svg
    assert "Trifolium repens" in svg
    assert "Lythrum salicaria" in svg
    assert "does not estimate a design-wide mean" in svg
    assert "direct BALANCE occupancy" in svg
