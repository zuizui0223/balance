"""Audit published Solanum architecture × bee-vibration mechanism evidence."""
from __future__ import annotations

import json

from balance_domain.solanum_mechanical_gate import (
    build_solanum_mechanical_gate_evidence,
)

if __name__ == "__main__":
    print(json.dumps(
        build_solanum_mechanical_gate_evidence(),
        ensure_ascii=False, sort_keys=True, indent=2,
    ))
