"""
ALFRED External Integrations

This module provides integrations with external services:
- GitHub: Issue creation, PR management, repository operations
- Slack: Notifications, alerts, team communication
- Jira: Ticket management (coming soon)
- PagerDuty: Incident management (coming soon)

Author: Daniel J Rita (BATDAN)
License: Proprietary - Part of ALFRED-UBX
"""

from .github_integration import GitHubIntegration
from .slack_integration import SlackIntegration

__all__ = [
    "GitHubIntegration",
    "SlackIntegration"
]
