"""Read-only original-paper fitted bee buzz/pollen release curves, no raw refit."""
from __future__ import annotations

import json
from balance_domain.solanum_buzz_source import build_solanum_published_kinetics_audit

if __name__ == "__main__":
    report = build_solanum_published_kinetics_audit()
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
