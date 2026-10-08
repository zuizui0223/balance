"""Stage-specific descriptive allocation slopes; never label as causal selection."""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Iterable, Mapping


def _number(row, key):
    raw = str(row.get(key, "") or "").strip()
    if not raw:
        return None
    x = float(raw)
    if not math.isfinite(x):
        raise ValueError("nonfinite " + key)
    return x


def stage_slopes(rows: Iterable[Mapping[str, str]]) -> dict:
    """Within plot-year weighted linear probability slopes on a common X scale.

    X is perfect-flower fraction of all flowers, a measured allocation proxy.
    This is an intentionally simple exploratory diagnostic, not the original
    standardized HflowerN selection gradient or a causal mediation estimate.
    """
    cells = defaultdict(list)
    for row in rows:
        h = _number(row, "perfect_flower_count")
        m = _number(row, "male_flower_count")
        initial = _number(row, "initial_fruit_count")
        final = _number(row, "intact_fruit_count")
        if h is None or m is None or h <= 0 or m < 0:
            continue
        if initial is None or final is None:
            continue
        if initial < 0 or final < 0 or initial > h or final > h:
            continue
        x = h / (h + m)
        cells[(row["year"], row["population_id"])].append(
            (x, initial / h, final / h, h))
    out = []
    for (year, plot), data in sorted(cells.items()):
        n = len(data)
        w = sum(z[3] for z in data)
        mx = sum(z[0]*z[3] for z in data)/w
        denom = sum(z[3]*(z[0]-mx)**2 for z in data)
        if n < 8 or denom <= 1e-12:
            out.append({"year":year,"plot":plot,"n":n,"status":"INSUFFICIENT_VARIATION"})
            continue
        slopes = []
        for idx in (1, 2):
            my = sum(z[idx]*z[3] for z in data)/w
            slopes.append(sum(z[3]*(z[0]-mx)*(z[idx]-my) for z in data)/denom)
        out.append({"year":year,"plot":plot,"n":n,
                    "beta_initial":slopes[0],"beta_final":slopes[1],
                    "delta":slopes[1]-slopes[0],"status":"DESCRIPTIVE_ONLY"})
    return {"schema_version":"PEUCEDANUM_STAGE_SLOPES_EXPLORATORY_V1",
            "cells":out,
            "claim_ceiling":"unadjusted_within_plot_year_allocation_associations_not_causal_or_BALANCE"}
