import pytest
from balance_domain.peucedanum_stage_slopes import stage_slopes


def test_paired_stage_slope_difference():
    rows=[]
    for i in range(20):
        h=10+i
        m=20-i
        rows.append({"year":"2022","population_id":"HA",
                     "perfect_flower_count":str(h),"male_flower_count":str(m),
                     "initial_fruit_count":str(round(h*(0.3+0.3*i/19))),
                     "intact_fruit_count":str(round(h*(0.2+0.1*i/19)))})
    x=stage_slopes(rows)["cells"][0]
    assert x["status"]=="DESCRIPTIVE_ONLY"
    assert x["n"]==20
    assert x["beta_initial"] > x["beta_final"]
    assert x["delta"] < 0


def test_missing_outcomes_not_imputed():
    rows=[{"year":"2021","population_id":"HA","perfect_flower_count":"4",
           "male_flower_count":"4","initial_fruit_count":"3",
           "intact_fruit_count":""}]
    assert stage_slopes(rows)["cells"] == []


def test_insufficient_variation_not_promoted():
    rows=[{"year":"2022","population_id":"HD","perfect_flower_count":"4",
           "male_flower_count":"4","initial_fruit_count":"3",
           "intact_fruit_count":"2"} for _ in range(12)]
    assert stage_slopes(rows)["cells"][0]["status"]=="INSUFFICIENT_VARIATION"
