"""Governance harness for ot-aiops — audit, policy, budget, undo, sanitize.

A self-contained, vendored governance layer. ot-aiops has NO dependency on
any external skill family — this package is its own copy of the harness:

  - ``@governed_tool`` — mandatory decorator on every MCP tool: policy pre-check,
    token/runaway budget guard, graduated-autonomy risk-tier gate, audit logging,
    and undo-token recording.
  - unified SQLite audit log under ``~/.ot-aiops/`` (override with
    ``OT_AIOPS_HOME``).
  - ``sanitize`` — prompt-injection defense for API-returned text.

State lives under ``ops_home()`` (default ``~/.ot-aiops``).
"""

from ot_aiops.governance.audit import AuditEngine, get_engine
from ot_aiops.governance.budget import BudgetExceeded, BudgetTracker, get_budget
from ot_aiops.governance.decorators import PolicyDenied, governed_tool
from ot_aiops.governance.patterns import Pattern, PatternMatch, get_pattern_engine
from ot_aiops.governance.policy import TierDecision, get_policy_engine
from ot_aiops.governance.sanitize import sanitize
from ot_aiops.governance.undo import UndoStore, get_undo_store

__all__ = [
    "governed_tool",
    "sanitize",
    "PolicyDenied",
    "get_engine",
    "AuditEngine",
    "get_policy_engine",
    "TierDecision",
    "get_budget",
    "BudgetTracker",
    "BudgetExceeded",
    "get_undo_store",
    "UndoStore",
    "Pattern",
    "PatternMatch",
    "get_pattern_engine",
]
