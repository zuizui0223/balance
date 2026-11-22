import os
import shutil
from pathlib import Path

import pytest

from balance_domain.solanum_bee_architecture import audit_rows, audit_source


CSV_NAME = "442_2022_5246_MOESM3_ESM.csv"
R_NAME = "442_2022_5246_MOESM2_ESM.r"


def bee(**changes):
    row = dict(
        BeeID="a", ColonyID="Blue", Treatment="Sham", HeadPollen="1",
        ThoraxPollen="2", AbdomenPollen="1", BodyPollen="4", StigmaPollen="2",
        PollinatingPollen="6", CorbiculaPollen="4", TotalPollen="10",
        HeadWidth="3.4", VisitTime="50", AntherPollen="60",
    )
    return {**row, **changes}


def test_each_bee_contributes_one_fraction_and_missingness_is_endpoint_specific():
    summary = audit_rows([
        bee(),
        bee(BeeID="b", HeadWidth="", AntherPollen="", CorbiculaPollen="12",
            TotalPollen="18"),
        bee(BeeID="c", Treatment="Cone"),
    ])
    free = summary["by_architecture"]["free"]
    endpoints = free["descriptives"]
    # Composite: (6/10 + 6/18)/2. Body only: (4/8 + 4/16)/2.
    assert endpoints["composite_fraction"]["mean"] == pytest.approx(7 / 15)
    assert endpoints["body_only_fraction"] == {"n": 2, "mean": 0.375, "se": 0.125}
    assert endpoints["AntherPollen"] == {"n": 1, "mean": 60, "se": None}
    assert endpoints["StigmaPollen"] == {"n": 2, "mean": 2, "se": 0}
    assert free["model_eligible_bees"]["basket"] == 1
    assert free["model_eligible_bees"]["anther"] == 1
    assert free["missing"]["HeadWidth"] == 1
    assert free["support"]["HeadWidth"] == {"n": 1, "min": 3.4, "max": 3.4}
    assert "provenance" not in summary


def test_missing_anther_alone_does_not_remove_a_bee_from_other_models():
    group = audit_rows([bee(AntherPollen=""), bee(BeeID="b")])["pooled"]
    assert group["model_eligible_bees"]["anther"] == 1
    assert all(n == 2 for k, n in group["model_eligible_bees"].items() if k != "anther")


@pytest.mark.parametrize("change, expected", [
    ({"BodyPollen": "3"}, "BodyPollen"),
    ({"PollinatingPollen": "5"}, "PollinatingPollen"),
    ({"TotalPollen": "9"}, "TotalPollen"),
    ({"CorbiculaPollen": "-1"}, "CorbiculaPollen"),
    ({"HeadPollen": "1.5"}, "HeadPollen"),
    ({"BeeID": "NA"}, "BeeID"),
    ({"Treatment": "unknown"}, "Treatment"),
    ({"VisitTime": "nan"}, "VisitTime"),
    ({"StigmaPollen": ""}, "StigmaPollen"),
])
def test_invalid_trial_or_inconsistent_pollen_count_is_rejected(change, expected):
    with pytest.raises(ValueError, match=expected):
        audit_rows([bee(**change)])


def test_duplicate_bee_id_is_rejected_even_across_colonies():
    with pytest.raises(ValueError, match="duplicate BeeID"):
        audit_rows([bee(), bee(ColonyID="Red")])


def test_missing_endpoint_column_is_not_an_allowed_missing_value():
    row = bee()
    del row["AntherPollen"]
    with pytest.raises(ValueError, match="column"):
        audit_rows([row])


@pytest.mark.parametrize("name,size", [(CSV_NAME, 5292), (R_NAME, 29899)])
def test_official_name_and_size_do_not_authenticate_changed_bytes(tmp_path, name, size):
    from balance_domain.solanum_bee_architecture import read_verified_file
    path = tmp_path / name
    path.write_bytes(b"x" * size)
    with pytest.raises(ValueError, match="SHA-256"):
        read_verified_file(path)


@pytest.mark.skipif(not os.getenv("WILKINS_SOURCE_DIR"), reason="publisher files not supplied")
def test_original_publisher_archive_reproduces_treatment_counts_and_table_one(tmp_path):
    source = Path(os.environ["WILKINS_SOURCE_DIR"])
    report = audit_source(source)
    assert report["pooled"]["n_bees"] == 60
    assert report["pooled"]["n_colonies"] == 3
    assert report["pooled"]["missing"] == {"HeadWidth": 1, "AntherPollen": 3}
    free, joined = (report["by_architecture"][a] for a in ["free", "joined"])
    assert (free["n_bees"], joined["n_bees"]) == (28, 32)
    assert (free["model_eligible_bees"]["anther"], joined["model_eligible_bees"]["anther"]) == (28, 29)
    assert (free["model_eligible_bees"]["basket"], joined["model_eligible_bees"]["basket"]) == (28, 31)
    fields = ["HeadPollen", "ThoraxPollen", "AbdomenPollen", "CorbiculaPollen",
              "AntherPollen", "StigmaPollen"]
    for group, means, ses in [
        (free, [1341, 23921, 8683, 211697, 252900, 3933],
         [237, 3256, 1578, 20452, 24095, 1055]),
        (joined, [868, 15254, 4846, 163949, 383540, 3220],
         [155, 1615, 522, 16120, 34421, 691]),
    ]:
        for field, printed_mean, printed_se in zip(fields, means, ses):
            endpoint = group["descriptives"][field]
            assert endpoint["mean"] == pytest.approx(printed_mean, abs=0.5)
            assert endpoint["se"] == pytest.approx(printed_se, abs=0.5)
    assert report["identity_checks"]["rows_checked"] == 60
    assert len(report["provenance"]["files"]) == 2
    shutil.copyfile(source / CSV_NAME, tmp_path / CSV_NAME)
    with pytest.raises(FileNotFoundError):
        audit_source(tmp_path)
