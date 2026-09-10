import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_impatiens_q1b_receipt_is_joint_ready_and_predeclared():
    r = json.loads((ROOT / "data" / "BALANCE_IMPATIENS_Q1B_RECEIPT_V1.json").read_text())
    assert r["effect_size_state"] == "JOINT_MULTICONTRAST_READY"
    assert r["q1b_positive_point_pattern_any_predeclared_trait"] is True
    assert r["n_complete"] == 85
    assert r["bootstrap_replicates"] == 2000
    assert r["joint_uncertainty_provenance"] == "stratified_raw_plant_bootstrap"
    assert r["traits_predeclared"] == ["Early_Season_Flower_Redness", "Early_Season_Condensed_Tannins"]
    for trait in r["traits_predeclared"]:
        x = r["traits"][trait]
        assert x["opposed_agent_point_pattern"] is True
        assert len(x["mediated_contrasts"]) == 4
        cov = x["mediated_contrast_covariance"]
        assert len(cov) == 4 and all(len(row) == 4 for row in cov)


def test_q1b_pooling_gate_is_open_at_three_of_three_after_gymnadenia():
    with (ROOT / "data" / "BALANCE_QUANTITATIVE_STRATA_V1.csv").open(newline="", encoding="utf-8") as fh:
        rows = {r["stratum_id"]: r for r in csv.DictReader(fh)}
    q1b = rows["DIFFUSE_FACTORIAL_AGENT_SELECTION"]
    assert int(q1b["min_independent_clusters"]) == 3
    assert int(q1b["effect_size_ready_clusters"]) == 3
    assert q1b["pooling_status"] == "POOLING_OPEN_FIRST_THREE_CLUSTER_POOL_FROZEN"
    assert "Fragaria_Impatiens_Gymnadenia" in q1b["next_gate"]
    assert "expand_independent_replication" in q1b["next_gate"]
