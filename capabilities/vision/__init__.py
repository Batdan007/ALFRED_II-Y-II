"""
Alfred's Vision System
Face recognition and camera integration

Author: Daniel J Rita (BATDAN)
"""

# Graceful import - only import if dependencies available
try:
    from .alfred_eyes import AlfredEyes
    __all__ = ['AlfredEyes']
    VISION_AVAILABLE = True
except ImportError:
    # Vision dependencies not installed (cv2, face_recognition, etc.)
    VISION_AVAILABLE = False
    __all__ = []
