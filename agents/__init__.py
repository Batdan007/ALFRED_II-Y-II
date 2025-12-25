"""
ALFRED Autonomous Agents

This module contains autonomous agents that implement the ReAct (Reasoning + Acting)
pattern for complex, multi-step tasks.

Available Agents:
- AlfredSecurityAgent: Autonomous security scanning and vulnerability management
- (More agents coming: ResearchAgent, DevOpsAgent, TradingAgent, ContentAgent)

Author: Daniel J Rita (BATDAN)
License: Proprietary - Part of ALFRED-UBX
"""

from .security_agent import (
    AlfredSecurityAgent,
    AgentState,
    ActionType,
    SecurityFinding,
    quick_security_scan
)

__all__ = [
    "AlfredSecurityAgent",
    "AgentState",
    "ActionType",
    "SecurityFinding",
    "quick_security_scan"
]
