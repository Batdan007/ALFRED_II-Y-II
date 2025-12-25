"""
ALFRED-UBX Core System
Privacy-first AI assistant with Alfred Brain in control
Author: Daniel J Rita (BATDAN)
"""

from .brain import AlfredBrain
from .path_manager import PathManager
from .config_loader import ConfigLoader
from .privacy_controller import PrivacyController
from .ui_launcher import UILauncher
from .context_manager import ContextManager

__all__ = [
    'AlfredBrain',
    'PathManager',
    'ConfigLoader',
    'PrivacyController',
    'UILauncher',
    'ContextManager'
]

__version__ = "3.0.0-ultimate"
__author__ = "Daniel J Rita (BATDAN)"
