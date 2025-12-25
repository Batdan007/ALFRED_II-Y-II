"""
Platform Utilities - Cross-Platform Helpers for Alfred AI Assistant

Provides platform detection, system information, and compatibility helpers.
"""

import platform
import sys
from typing import Dict, Literal

PlatformType = Literal['Windows', 'macOS', 'Linux', 'Unknown']


def get_platform_name() -> PlatformType:
    """
    Get the platform name in human-readable form.

    Returns:
        'Windows', 'macOS', 'Linux', or 'Unknown'
    """
    system = platform.system()

    if system == 'Windows':
        return 'Windows'
    elif system == 'Darwin':
        return 'macOS'
    elif system == 'Linux':
        return 'Linux'
    else:
        return 'Unknown'


def is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system() == 'Windows'


def is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system() == 'Darwin'


def is_linux() -> bool:
    """Check if running on Linux."""
    return platform.system() == 'Linux'


def is_mobile() -> bool:
    """
    Check if running on mobile platform (iOS, Android).

    Note: This is a best-effort detection.
    """
    # iOS detection
    if platform.system() == 'Darwin' and 'iphone' in platform.machine().lower():
        return True

    # Android detection (when running in Termux or similar)
    try:
        import os
        return 'ANDROID_ROOT' in os.environ or 'ANDROID_DATA' in os.environ
    except:
        return False


def get_platform_info() -> Dict[str, any]:
    """
    Get comprehensive platform information.

    Returns:
        Dictionary containing platform details:
        - system: Raw platform.system() value
        - system_name: Human-readable platform name
        - release: OS release version
        - version: OS version details
        - machine: Machine architecture
        - processor: Processor name
        - python_version: Python version
        - python_implementation: Python implementation (CPython, PyPy, etc.)
        - is_windows: Boolean
        - is_macos: Boolean
        - is_linux: Boolean
        - is_mobile: Boolean
        - is_64bit: Boolean
    """
    return {
        # Platform info
        'system': platform.system(),
        'system_name': get_platform_name(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),

        # Python info
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
        'python_compiler': platform.python_compiler(),

        # Platform checks
        'is_windows': is_windows(),
        'is_macos': is_macos(),
        'is_linux': is_linux(),
        'is_mobile': is_mobile(),
        'is_64bit': sys.maxsize > 2**32,

        # Additional info
        'hostname': platform.node(),
        'architecture': platform.architecture()[0],
    }


def get_platform_emoji() -> str:
    """
    Get a platform-specific emoji.

    Returns:
        Emoji representing the current platform
    """
    system_name = get_platform_name()

    emoji_map = {
        'Windows': '🪟',
        'macOS': '🍎',
        'Linux': '🐧',
        'Unknown': '❓'
    }

    return emoji_map.get(system_name, '💻')


def print_platform_info():
    """Print formatted platform information."""
    info = get_platform_info()

    # Try to use emoji, fallback to text if encoding issues
    try:
        emoji = get_platform_emoji()
        print("\n" + "="*60)
        print(f"{emoji} Alfred Platform Information")
        print("="*60)
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Windows console encoding fallback
        print("\n" + "="*60)
        print(f"Alfred Platform Information ({info['system_name']})")
        print("="*60)
    print(f"\nPlatform:")
    print(f"  System:       {info['system_name']} ({info['system']})")
    print(f"  Release:      {info['release']}")
    print(f"  Architecture: {info['machine']} ({info['architecture']})")
    print(f"  Hostname:     {info['hostname']}")
    print(f"\nPython:")
    print(f"  Version:        {info['python_version']}")
    print(f"  Implementation: {info['python_implementation']}")
    print(f"  Compiler:       {info['python_compiler']}")
    print(f"\nCapabilities:")
    print(f"  64-bit:  {info['is_64bit']}")
    print(f"  Mobile:  {info['is_mobile']}")
    print("="*60 + "\n")


def get_recommended_voice_for_platform() -> str:
    """
    Get recommended voice engine for current platform.

    Returns:
        Recommended voice engine name
    """
    if is_windows():
        return 'pyttsx3_sapi5'  # Microsoft SAPI5 voices (Ryan, George)
    elif is_macos():
        return 'pyttsx3_nsss'   # macOS NSSpeechSynthesizer (Daniel, Alex)
    elif is_linux():
        return 'pyttsx3_espeak' # eSpeak with en-gb accent
    else:
        return 'pyttsx3_default'


def get_platform_specific_path_separator() -> str:
    """
    Get the platform-specific path separator.

    Returns:
        '\\' for Windows, '/' for Unix-like systems
    """
    import os
    return os.sep


def supports_voice() -> bool:
    """
    Check if the platform supports voice synthesis.

    Returns:
        True if voice is supported, False otherwise
    """
    try:
        import pyttsx3
        # Try to initialize engine
        engine = pyttsx3.init()
        engine.stop()
        return True
    except:
        return False


def supports_emoji() -> bool:
    """
    Check if the platform supports emoji display.

    Returns:
        True if emojis are supported
    """
    # Windows 10+ supports emoji, older Windows may not
    if is_windows():
        try:
            version = int(platform.release())
            return version >= 10
        except:
            return False

    # macOS and Linux generally support emoji
    return is_macos() or is_linux()


if __name__ == "__main__":
    # Test platform utilities
    print("Testing Platform Utilities...")
    print()

    # Print full platform info
    print_platform_info()

    # Test individual functions
    print("Individual Tests:")
    print(f"  Platform Name: {get_platform_name()}")
    print(f"  Is Windows: {is_windows()}")
    print(f"  Is macOS: {is_macos()}")
    print(f"  Is Linux: {is_linux()}")
    print(f"  Is Mobile: {is_mobile()}")
    print(f"  Recommended Voice: {get_recommended_voice_for_platform()}")
    print(f"  Supports Voice: {supports_voice()}")
    print(f"  Supports Emoji: {supports_emoji()}")
    try:
        print(f"  Platform Emoji: {get_platform_emoji()}")
    except (UnicodeEncodeError, UnicodeDecodeError):
        print(f"  Platform Emoji: [Windows console encoding issue - emoji available in UTF-8]")
