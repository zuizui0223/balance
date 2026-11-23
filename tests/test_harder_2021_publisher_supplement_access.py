"""Only synthetic ZIP fixtures, verifying journal-supplement source ceilings."""
from io import BytesIO
import zipfile

import pytest

from scripts.audit_harder_2021_publisher_supplements import (
    URL, inspect_publisher_zip
)


def synthetic_zip():
    buff=BytesIO()
    with zipfile.ZipFile(buff,"w") as z:
        z.writestr("model.R",(
            "# Synthetic unit-test model, NOT real author code.\n"
            "data <- read.csv('Data_for_AmNat.csv')\n"
            "data <- subset(data,Trial>1 & Trial_type=='Emasc')\n"
        ))
        z.writestr("manual.txt","Source trial labels and analysis manual\n")
    return buff.getvalue()


def test_official_original_supplement_link_is_source_only():
    assert URL=="https://www.journals.uchicago.edu/doi/suppl/10.1086/712378/suppl_file/59424Supplements.zip"
    got=inspect_publisher_zip(synthetic_zip())
    assert got["status"]=="PUBLISHER_ZIP_DOWNLOADED_METADATA_INSPECTED_NOT_EXECUTED"
    assert got["zip_file_count"]==2
    assert got["original_effect_models_refitted"] is False
    assert got["verifies_original_31_trial_inclusion"] is False
    assert all("path" in x and "bytes" in x for x in got["member_inventory"])
    x=next(row for row in got["member_inventory"] if row["path"]=="model.R")
    assert x["keyword_line_counts"]["trial_id"]>0
    assert x["keyword_line_counts"]["source_file"]>0
    assert x["contains_usable_trial_admission_rule"]=="UNDETERMINED_BY_METADATA"
    assert "Synthetic unit-test model" not in str(got)


def test_html_or_non_archive_fails_closed():
    with pytest.raises(ValueError,match="bounded ZIP"):
        inspect_publisher_zip(b"<html>blocked</html>")
