"""
Privacy Controller - Manages local vs cloud AI access
Ensures 100% local by default with explicit user control for cloud features
Author: Daniel J Rita (BATDAN)
"""

import logging
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime


class PrivacyMode(Enum):
    """Privacy operation modes"""
    LOCAL = "local"           # 100% local, no internet
    HYBRID = "hybrid"         # Local + cloud when explicitly requested
    CLOUD = "cloud"           # Cloud AI enabled


class CloudProvider(Enum):
    """Available cloud AI providers"""
    CLAUDE = "claude"
    OPENAI = "openai"
    GROQ = "groq"


class PrivacyController:
    """
    Controls privacy settings and manages local vs cloud AI access.

    Key Features:
    - 100% local by default
    - Explicit user confirmation for cloud access
    - Status tracking (local/online)
    - Session history of privacy decisions
    """

    def __init__(self, default_mode: PrivacyMode = PrivacyMode.LOCAL,
                 auto_confirm: bool = False):
        """
        Initialize privacy controller

        Args:
            default_mode: Default privacy mode (LOCAL by default)
            auto_confirm: Auto-confirm cloud requests (False by default for safety)
        """
        self.logger = logging.getLogger(__name__)
        self.current_mode = default_mode
        self.auto_confirm = auto_confirm

        # Track enabled cloud providers
        self.enabled_providers: Dict[CloudProvider, bool] = {
            CloudProvider.CLAUDE: False,
            CloudProvider.OPENAI: False,
            CloudProvider.GROQ: False
        }

        # Session history
        self.session_history: List[Dict] = []

        self.logger.info(f"Privacy Controller initialized in {default_mode.value.upper()} mode")

    def is_local_only(self) -> bool:
        """Check if currently in local-only mode"""
        return self.current_mode == PrivacyMode.LOCAL

    def is_cloud_enabled(self) -> bool:
        """Check if any cloud provider is enabled"""
        return any(self.enabled_providers.values())

    def get_status_icon(self) -> str:
        """Get status icon for display"""
        if self.is_local_only():
            return "🔒 LOCAL"
        elif self.is_cloud_enabled():
            return "🌐 ONLINE"
        else:
            return "🔒 LOCAL"

    def request_cloud_access(self, provider: CloudProvider,
                            reason: str = "") -> bool:
        """
        Request access to cloud AI provider

        Args:
            provider: Cloud provider to enable
            reason: Reason for request (for logging/confirmation)

        Returns:
            True if approved, False if denied
        """
        if self.auto_confirm:
            return self._enable_provider(provider, reason)

        # Log request
        self.logger.warning(
            f"Cloud access requested: {provider.value}\n"
            f"   Reason: {reason}\n"
            f"   This will send data to {provider.value} servers."
        )

        # In real implementation, this would prompt user
        # For now, return False (deny) to maintain privacy
        return False

    def _enable_provider(self, provider: CloudProvider, reason: str = "") -> bool:
        """Enable a cloud provider"""
        self.enabled_providers[provider] = True
        self.current_mode = PrivacyMode.HYBRID

        # Log decision
        self.session_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'enable_provider',
            'provider': provider.value,
            'reason': reason
        })

        self.logger.info(f"{provider.value} enabled | {reason}")
        return True

    def disable_provider(self, provider: CloudProvider):
        """Disable a cloud provider"""
        self.enabled_providers[provider] = False

        # If all disabled, return to local mode
        if not any(self.enabled_providers.values()):
            self.current_mode = PrivacyMode.LOCAL
            self.logger.info("All cloud providers disabled - returned to LOCAL mode")

        self.session_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'disable_provider',
            'provider': provider.value
        })

    def enable_multimodel(self, providers: Optional[List[CloudProvider]] = None) -> bool:
        """
        Enable multi-model mode (multiple cloud providers)

        Args:
            providers: List of providers to enable (default: all)

        Returns:
            True if enabled, False if user denied
        """
        if providers is None:
            providers = list(CloudProvider)

        self.logger.warning(
            "Multi-model mode requested\n"
            f"   Providers: {[p.value for p in providers]}\n"
            "   This will send your queries to multiple cloud services."
        )

        if self.auto_confirm:
            for provider in providers:
                self._enable_provider(provider, "multi-model mode")
            return True

        # In real implementation, prompt user
        return False

    def disable_all_cloud(self):
        """Disable all cloud providers and return to local mode"""
        for provider in CloudProvider:
            self.enabled_providers[provider] = False

        self.current_mode = PrivacyMode.LOCAL
        self.logger.info("All cloud providers disabled - LOCAL mode active")

        self.session_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'disable_all_cloud'
        })

    def get_status(self) -> Dict:
        """Get current privacy status"""
        return {
            'mode': self.current_mode.value,
            'status_icon': self.get_status_icon(),
            'local_only': self.is_local_only(),
            'cloud_enabled': self.is_cloud_enabled(),
            'enabled_providers': [
                p.value for p, enabled in self.enabled_providers.items() if enabled
            ],
            'session_requests': len(self.session_history)
        }

    def get_session_summary(self) -> str:
        """Get session privacy summary"""
        status = self.get_status()

        summary = [
            f"\n{'='*60}",
            f"PRIVACY SESSION SUMMARY",
            f"{'='*60}",
            f"Current Mode: {status['status_icon']} {status['mode'].upper()}",
            f"Local Only: {'Yes' if status['local_only'] else 'No'}",
            f"Cloud Enabled: {'Yes' if status['cloud_enabled'] else 'No'}",
        ]

        if status['enabled_providers']:
            summary.append(f"Active Providers: {', '.join(status['enabled_providers'])}")

        summary.append(f"Session Requests: {status['session_requests']}")
        summary.append(f"{'='*60}\n")

        return '\n'.join(summary)


# Convenience functions
def create_local_controller() -> PrivacyController:
    """Create a privacy controller in strict local mode"""
    return PrivacyController(
        default_mode=PrivacyMode.LOCAL,
        auto_confirm=False
    )


def create_hybrid_controller(auto_confirm: bool = False) -> PrivacyController:
    """Create a privacy controller in hybrid mode"""
    return PrivacyController(
        default_mode=PrivacyMode.HYBRID,
        auto_confirm=auto_confirm
    )
