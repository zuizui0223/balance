from balance_domain.monochoria_sequence_inventory import classify_record


def test_classify_complete_plastome():
    assert (
        classify_record(
            "Pontederia cyanea chloroplast, complete genome",
            150000,
            ["rbcL", "ndhF", "ycf1"],
        )
        == "COMPLETE_PLASTOME"
    )


def test_classify_additional_locus():
    assert classify_record("partial sequence", 900, ["ycf1"]) == "ADDITIONAL_ANNOTATED_LOCUS"


def test_classify_current_markers_only():
    assert classify_record("partial cds", 1400, ["rbcL"]) == "CURRENT_MARKER_ONLY"
    assert classify_record("partial cds", 600, ["ndhF"]) == "CURRENT_MARKER_ONLY"


def test_classify_unannotated_long_record():
    assert classify_record("genomic sequence", 9000, []) == "OTHER_LONG_RECORD"
