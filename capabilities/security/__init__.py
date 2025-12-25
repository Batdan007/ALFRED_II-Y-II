"""
Alfred's Security Capabilities
Strix scanner integration and security analysis

Author: Daniel J Rita (BATDAN)
"""

# Graceful import - only import if Strix is installed
try:
    from .strix_scanner import StrixScanner, ScanType
    __all__ = ['StrixScanner', 'ScanType']
    SECURITY_AVAILABLE = True
except ImportError:
    # Strix not installed (optional dependency)
    SECURITY_AVAILABLE = False
    __all__ = []
