"""Core API for Chapter 2 BALANCE-domain analysis."""

from .static import BalancePathResult, analyze_balance_path
from .dynamics import SwitchingCostResult, switching_cost_state

__all__ = [
    "BalancePathResult",
    "SwitchingCostResult",
    "analyze_balance_path",
    "switching_cost_state",
]
