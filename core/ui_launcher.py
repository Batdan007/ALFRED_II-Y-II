"""
UI Launcher - Smart browser launching for visual content
Only opens UI when explicitly needed for visual tasks
Author: Daniel J Rita (BATDAN)
"""

import logging
import webbrowser
import subprocess
from enum import Enum
from typing import Optional, Dict, List
from pathlib import Path


class UIMode(Enum):
    """UI display modes"""
    VISUAL_VIEWER = "visual_viewer"           # For diagrams, schematics, images
    MULTIMODEL_DASHBOARD = "multimodel"       # Multi-model comparison
    DOCUMENT_VIEWER = "document_viewer"       # Building plans, PDFs
    AGENT_DASHBOARD = "agent_dashboard"       # Enterprise agent status
    MISSION_CONTROL = "mission_control"       # Full dashboard


class UILauncher:
    """
    Smart UI launcher that opens browser windows only when needed.

    Key Features:
    - Detects visual content requests
    - Launches minimal UI for specific tasks
    - Closes UI when done
    - Tracks active UI windows
    """

    # Visual trigger keywords
    VISUAL_TRIGGERS = [
        "show", "display", "diagram", "schematic", "blueprint", "plans",
        "chart", "graph", "visualize", "render", "draw", "image", "photo",
        "wiring", "circuit", "building", "floor plan", "layout"
    ]

    # Dashboard trigger keywords
    DASHBOARD_TRIGGERS = [
        "dashboard", "status", "monitor", "overview", "summary"
    ]

    # Multi-model trigger keywords
    MULTIMODEL_TRIGGERS = [
        "compare models", "multi-model", "multimodel", "compare ai",
        "all models", "multiple ais"
    ]

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize UI launcher

        Args:
            base_url: Base URL for UI server
        """
        self.logger = logging.getLogger(__name__)
        self.base_url = base_url
        self.active_windows: Dict[UIMode, bool] = {}
        self.ui_enabled = True

    def should_launch_ui(self, user_input: str) -> Optional[UIMode]:
        """
        Determine if UI should be launched based on user input

        Args:
            user_input: User's message

        Returns:
            UIMode to launch, or None if no UI needed
        """
        user_input_lower = user_input.lower()

        # Check for multi-model comparison
        if any(trigger in user_input_lower for trigger in self.MULTIMODEL_TRIGGERS):
            return UIMode.MULTIMODEL_DASHBOARD

        # Check for agent dashboard
        if any(trigger in user_input_lower for trigger in self.DASHBOARD_TRIGGERS):
            # If asking about agents, launch agent dashboard
            if "agent" in user_input_lower or "github" in user_input_lower or "jira" in user_input_lower:
                return UIMode.AGENT_DASHBOARD
            # Otherwise, mission control
            return UIMode.MISSION_CONTROL

        # Check for visual content
        if any(trigger in user_input_lower for trigger in self.VISUAL_TRIGGERS):
            # Determine specific visual mode
            if "building" in user_input_lower or "floor plan" in user_input_lower or "blueprint" in user_input_lower:
                return UIMode.DOCUMENT_VIEWER
            else:
                return UIMode.VISUAL_VIEWER

        # No UI needed
        return None

    def launch_ui(self, mode: UIMode, content: Optional[Dict] = None) -> bool:
        """
        Launch UI in specific mode

        Args:
            mode: UI mode to launch
            content: Optional content to display

        Returns:
            True if launched successfully, False otherwise
        """
        if not self.ui_enabled:
            self.logger.warning("UI launching is disabled")
            return False

        try:
            # Build URL based on mode
            url = self._build_url(mode, content)

            # Log launch
            self.logger.info(f"👁️ Launching {mode.value} UI at {url}")

            # Open browser
            webbrowser.open(url)

            # Track active window
            self.active_windows[mode] = True

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to launch UI: {e}")
            return False

    def _build_url(self, mode: UIMode, content: Optional[Dict] = None) -> str:
        """Build URL for specific UI mode"""
        base = self.base_url

        url_map = {
            UIMode.VISUAL_VIEWER: f"{base}/visual",
            UIMode.MULTIMODEL_DASHBOARD: f"{base}/multimodel",
            UIMode.DOCUMENT_VIEWER: f"{base}/documents",
            UIMode.AGENT_DASHBOARD: f"{base}/agents",
            UIMode.MISSION_CONTROL: f"{base}/mission-control"
        }

        url = url_map.get(mode, base)

        # Add content parameters if provided
        if content:
            params = "&".join([f"{k}={v}" for k, v in content.items()])
            url = f"{url}?{params}"

        return url

    def close_ui(self, mode: Optional[UIMode] = None):
        """
        Close UI window(s)

        Args:
            mode: Specific mode to close, or None to close all
        """
        if mode:
            self.active_windows[mode] = False
            self.logger.info(f"Closed {mode.value} UI")
        else:
            self.active_windows.clear()
            self.logger.info("Closed all UI windows")

    def is_ui_active(self, mode: Optional[UIMode] = None) -> bool:
        """
        Check if UI is currently active

        Args:
            mode: Specific mode to check, or None to check any

        Returns:
            True if UI is active, False otherwise
        """
        if mode:
            return self.active_windows.get(mode, False)
        return any(self.active_windows.values())

    def get_active_uis(self) -> List[UIMode]:
        """Get list of currently active UI modes"""
        return [mode for mode, active in self.active_windows.items() if active]

    def enable_ui(self):
        """Enable UI launching"""
        self.ui_enabled = True
        self.logger.info("UI launching enabled")

    def disable_ui(self):
        """Disable UI launching (terminal-only mode)"""
        self.ui_enabled = False
        self.close_ui()  # Close any active UIs
        self.logger.info("UI launching disabled - terminal-only mode")

    def get_status(self) -> Dict:
        """Get UI launcher status"""
        return {
            'enabled': self.ui_enabled,
            'active_windows': len(self.active_windows),
            'active_modes': [mode.value for mode in self.get_active_uis()],
            'base_url': self.base_url
        }


# Convenience function
def create_ui_launcher(enabled: bool = True, base_url: str = "http://localhost:8000") -> UILauncher:
    """Create a UI launcher with specified settings"""
    launcher = UILauncher(base_url=base_url)
    if not enabled:
        launcher.disable_ui()
    return launcher
