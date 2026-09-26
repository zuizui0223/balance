from balance_domain.diascia_its_audit import (
    is_exact_species_name,
    its_record_score,
    select_representatives,
)


def test_exact_species_name_rejects_open_nomenclature():
    assert is_exact_species_name("Diascia anastrepta") is True
    assert is_exact_species_name("Diascia barberae") is True
    assert is_exact_species_name("Diascia sp. ABC") is False
    assert is_exact_species_name("Diascia cf. barberae") is False
    assert is_exact_species_name("Alonsoa unilabiata") is False


def test_full_its_record_scores_above_partial_its_record():
    full = its_record_score(
        "Diascia anastrepta internal transcribed spacer 1, 5.8S ribosomal RNA gene "
        "and internal transcribed spacer 2, complete sequence",
        "A" * 650,
        "ABC1.1",
    )
    partial = its_record_score(
        "Diascia anastrepta internal transcribed spacer 1, partial sequence",
        "A" * 500,
        "ABC2.1",
    )
    assert full > partial


def test_select_representatives_is_outcome_blind_and_prefers_complete_its():
    records = [
        {
            "taxon": "Diascia anastrepta",
            "accession": "B.1",
            "description": "Diascia anastrepta ITS1 partial sequence",
            "sequence": "A" * 500,
        },
        {
            "taxon": "Diascia anastrepta",
            "accession": "A.1",
            "description": (
                "Diascia anastrepta internal transcribed spacer 1, 5.8S "
                "ribosomal RNA gene and internal transcribed spacer 2"
            ),
            "sequence": "A" * 650,
        },
        {
            "taxon": "Diascia sp. WNH1",
            "accession": "C.1",
            "description": "Diascia sp. WNH1 ITS sequence",
            "sequence": "A" * 650,
        },
    ]
    selected = select_representatives(records)
    assert set(selected) == {"Diascia anastrepta"}
    assert selected["Diascia anastrepta"]["accession"] == "A.1"
