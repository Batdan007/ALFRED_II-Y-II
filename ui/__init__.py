"""
ALFRED UI Module

Cross-platform user interface components:
- Chat interface with brain integration
- System tray for quick access
- Modern glassmorphism design

Author: Daniel J Rita (BATDAN)
Part of ALFRED-UBX / BATCOMPUTER AI Ecosystem
"""

try:
    from .system_tray import AlfredSystemTray, create_tray, run_tray
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

__all__ = [
    "AlfredSystemTray",
    "create_tray",
    "run_tray",
    "TRAY_AVAILABLE"
]
