"""Conditional female seed-fitness threshold check, not a structural payoff fit.

Ramsey, Vaughton & Peakall (2006; doi:10.1111/j.1420-9101.2006.01129.x)
report 3.7 vs 1.4 female relative reproductive advantage under two
pollination/outcrossing regimes in Wurmbea dioica. Simple twofold nuclear
and onefold strictly maternal transmission thresholds are illustrations
from classical gynodioecy theory; neither is directly identified for the
actual Wurmbea sex-determination and high-inbreeding system.

The module does not turn ratio data into R, K, Phi, a selection gradient,
an invasion rate, a confidence interval, or a historical transition.
"""
from __future__ import annotations

from math import isfinite, log

SOURCE_DOI = "10.1111/j.1420-9101.2006.01129.x"
REGIMES = {
    "OPEN_FEMALE_ADVANTAGE": 3.7,
    "MALE_OUTCROSSING_INCREASED_FEMALE_ADVANTAGE": 1.4,
}
BENCHMARKS = {
    "SIMPLE_BIPARENTAL_NUCLEAR_TWOFOLD": 2.0,
    "STRICTLY_MATERNAL_NO_RESTORER_IDEALIZED_ONEFOLD": 1.0,
}


def classify_advantage(value: float, threshold: float) -> str:
    if not isfinite(value) or value <= 0 or not isfinite(threshold) or threshold <= 0:
        raise ValueError("positive finite reproductive ratio and threshold required")
    if value > threshold:
        return "ABOVE_ASSUMED_THRESHOLD"
    if value < threshold:
        return "BELOW_ASSUMED_THRESHOLD"
    return "AT_ASSUMED_THRESHOLD"


def analyze_thresholds(benchmark_thresholds: dict[str, float] = BENCHMARKS) -> dict:
    high = REGIMES["OPEN_FEMALE_ADVANTAGE"]
    low = REGIMES["MALE_OUTCROSSING_INCREASED_FEMALE_ADVANTAGE"]
    if not high > low > 0:
        raise ValueError("source direction unexpectedly changed")
    result = {}
    for label, threshold in benchmark_thresholds.items():
        comparisons = {
            regime: {
                "source_ratio": ratio,
                "assumed_threshold": threshold,
                "ratio_over_threshold": ratio / threshold,
                "log_ratio_over_threshold": log(ratio / threshold),
                "classification": classify_advantage(ratio, threshold),
            }
            for regime, ratio in REGIMES.items()
        }
        result[label] = {
            "comparisons": comparisons,
            "regime_classification_changes": (
                comparisons["OPEN_FEMALE_ADVANTAGE"]["classification"]
                != comparisons["MALE_OUTCROSSING_INCREASED_FEMALE_ADVANTAGE"]["classification"]
            ),
            "not_observed_heritable_invasion": True,
        }
    return {
        "schema": "BALANCE_WURMBEA_REPRODUCTIVE_RATIO_THRESHOLD_BOUNDS_V1",
        "source": {"doi": SOURCE_DOI, "female_seed_fitness_advantage_regimes": REGIMES},
        "relative_ratio_change": high / low,
        "ratio_decline_fraction": 1.0 - low / high,
        "thresholds_for_a_strict_change_of_side": {
            "strictly_greater_than": low,
            "strictly_less_than": high,
        },
        "assumption_specific_results": result,
        "claims_that_are_not_identified": [
            "actual sex determination and fitness transmission threshold in Wurmbea",
            "confidence interval for a source ratio or its difference",
            "full maternal plus paternal lifetime reproductive fitness",
            "independent new modular architecture construction or maintenance cost",
            "invasion/fixation/occupancy of a sex-determining genotype",
            "historical transition from shared to differentiated sexual architecture",
        ],
        "interpretation": (
            "The observed ratio crosses a hypothetical inheritance benchmark "
            "exactly when that threshold lies strictly between 1.4 and 3.7. "
            "This is a conditional threshold diagnostic, not a result about "
            "the true Wurmbea invasion threshold."
        ),
    }
