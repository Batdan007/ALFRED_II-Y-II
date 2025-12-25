"""
Path Manager - Centralized Path Management for Alfred AI Assistant

Cross-platform path management:
- Windows: C:/Drive
- macOS: ~/Library/Application Support/Alfred
- Linux: ~/.alfred
- iOS: App sandbox

Override with ALFRED_HOME environment variable.
"""

import os
import platform
from pathlib import Path
from typing import Dict, Optional


def _get_platform_root() -> Path:
    """
    Determine the appropriate root directory based on platform.

    Returns:
        Path to the platform-specific Alfred root directory
    """
    # Check for environment variable override first
    if os.getenv('ALFRED_HOME'):
        return Path(os.getenv('ALFRED_HOME'))

    system = platform.system()

    if system == 'Windows':
        # Windows: C:/Drive (original behavior)
        return Path("C:/Drive")
    elif system == 'Darwin':  # macOS
        # macOS: ~/Library/Application Support/Alfred
        return Path.home() / "Library" / "Application Support" / "Alfred"
    elif system == 'Linux':
        # Linux: ~/.alfred
        return Path.home() / ".alfred"
    else:
        # Unknown platform: use home directory
        return Path.home() / ".alfred"


class PathManager:
    """
    Centralized cross-platform path management for Alfred AI Assistant.

    Platform-specific roots:
    - Windows: C:/Drive
    - macOS: ~/Library/Application Support/Alfred
    - Linux: ~/.alfred
    - iOS: App sandbox storage

    Override with ALFRED_HOME environment variable for custom location.
    """

    # Root directory (dynamically determined)
    DRIVE_ROOT = _get_platform_root()

    # ========================================
    # MODELS
    # ========================================
    MODELS_DIR = DRIVE_ROOT / "models"
    OLLAMA_MODELS_DIR = MODELS_DIR / "ollama"
    VOICE_MODELS_DIR = MODELS_DIR / "voice"
    VISION_MODELS_DIR = MODELS_DIR / "vision"
    EMBEDDINGS_MODELS_DIR = MODELS_DIR / "embeddings"

    # ========================================
    # DATA
    # ========================================
    DATA_DIR = DRIVE_ROOT / "data"
    BRAIN_DB = DATA_DIR / "alfred_brain.db"
    VECTOR_STORE_DIR = DATA_DIR / "vector_store"
    CACHE_DIR = DATA_DIR / "cache"
    CONVERSATIONS_DIR = DATA_DIR / "conversations"
    KNOWLEDGE_DIR = DATA_DIR / "knowledge"

    # ========================================
    # CONFIGURATION
    # ========================================
    CONFIG_DIR = DRIVE_ROOT / "config"
    ALFRED_CONFIG = CONFIG_DIR / "alfred.yaml"
    MODELS_CONFIG = CONFIG_DIR / "models.yaml"
    INTEGRATIONS_CONFIG = CONFIG_DIR / "integrations.yaml"
    PATHS_CONFIG = CONFIG_DIR / "paths.yaml"
    ENV_FILE = CONFIG_DIR / ".env"

    # ========================================
    # FABRIC AI PATTERNS
    # ========================================
    FABRIC_DIR = DRIVE_ROOT / "fabric"
    FABRIC_PATTERNS_DIR = FABRIC_DIR / "patterns"

    # ========================================
    # LOGS
    # ========================================
    LOGS_DIR = DRIVE_ROOT / "logs"
    ALFRED_LOGS_DIR = LOGS_DIR / "alfred"
    INTEGRATIONS_LOGS_DIR = LOGS_DIR / "integrations"
    ERRORS_LOGS_DIR = LOGS_DIR / "errors"

    # ========================================
    # BACKUPS
    # ========================================
    BACKUPS_DIR = DRIVE_ROOT / "backups"
    DAILY_BACKUPS_DIR = BACKUPS_DIR / "daily"
    WEEKLY_BACKUPS_DIR = BACKUPS_DIR / "weekly"

    @classmethod
    def ensure_all_paths(cls) -> Dict[str, bool]:
        """
        Ensure all directories exist.

        Returns:
            Dict of path names and their creation status
        """
        paths_to_create = [
            # Models
            cls.MODELS_DIR,
            cls.OLLAMA_MODELS_DIR,
            cls.VOICE_MODELS_DIR,
            cls.VISION_MODELS_DIR,
            cls.EMBEDDINGS_MODELS_DIR,

            # Data
            cls.DATA_DIR,
            cls.VECTOR_STORE_DIR,
            cls.CACHE_DIR,
            cls.CONVERSATIONS_DIR,
            cls.KNOWLEDGE_DIR,

            # Config
            cls.CONFIG_DIR,

            # Fabric
            cls.FABRIC_DIR,
            cls.FABRIC_PATTERNS_DIR,

            # Logs
            cls.LOGS_DIR,
            cls.ALFRED_LOGS_DIR,
            cls.INTEGRATIONS_LOGS_DIR,
            cls.ERRORS_LOGS_DIR,

            # Backups
            cls.BACKUPS_DIR,
            cls.DAILY_BACKUPS_DIR,
            cls.WEEKLY_BACKUPS_DIR,
        ]

        results = {}
        for path in paths_to_create:
            try:
                path.mkdir(parents=True, exist_ok=True)
                results[str(path)] = True
            except Exception as e:
                results[str(path)] = False
                print(f"⚠ Failed to create {path}: {e}")

        return results

    @classmethod
    def get_model_path(cls, model_type: str, model_name: str) -> Path:
        """
        Get path to a specific model.

        Args:
            model_type: 'ollama', 'voice', 'vision', or 'embeddings'
            model_name: Name of the model

        Returns:
            Path to the model
        """
        model_dirs = {
            'ollama': cls.OLLAMA_MODELS_DIR,
            'voice': cls.VOICE_MODELS_DIR,
            'vision': cls.VISION_MODELS_DIR,
            'embeddings': cls.EMBEDDINGS_MODELS_DIR,
        }

        if model_type not in model_dirs:
            raise ValueError(f"Unknown model type: {model_type}")

        return model_dirs[model_type] / model_name

    @classmethod
    def get_log_file(cls, log_type: str, filename: str) -> Path:
        """
        Get path to a log file.

        Args:
            log_type: 'alfred', 'integrations', or 'errors'
            filename: Log filename

        Returns:
            Path to the log file
        """
        log_dirs = {
            'alfred': cls.ALFRED_LOGS_DIR,
            'integrations': cls.INTEGRATIONS_LOGS_DIR,
            'errors': cls.ERRORS_LOGS_DIR,
        }

        if log_type not in log_dirs:
            raise ValueError(f"Unknown log type: {log_type}")

        return log_dirs[log_type] / filename

    @classmethod
    def get_backup_path(cls, backup_type: str, filename: str) -> Path:
        """
        Get path to a backup file.

        Args:
            backup_type: 'daily' or 'weekly'
            filename: Backup filename

        Returns:
            Path to the backup file
        """
        backup_dirs = {
            'daily': cls.DAILY_BACKUPS_DIR,
            'weekly': cls.WEEKLY_BACKUPS_DIR,
        }

        if backup_type not in backup_dirs:
            raise ValueError(f"Unknown backup type: {backup_type}")

        return backup_dirs[backup_type] / filename

    @classmethod
    def verify_drive_access(cls) -> bool:
        """
        Verify that C:/Drive is accessible and writable.

        Returns:
            True if accessible, False otherwise
        """
        try:
            # Check if root exists
            if not cls.DRIVE_ROOT.exists():
                print(f"⚠ {cls.DRIVE_ROOT} does not exist")
                return False

            # Try to create a test file
            test_file = cls.DRIVE_ROOT / ".access_test"
            test_file.write_text("access test")
            test_file.unlink()

            return True
        except Exception as e:
            print(f"⚠ Cannot access {cls.DRIVE_ROOT}: {e}")
            return False

    @classmethod
    def get_stats(cls) -> Dict[str, any]:
        """
        Get storage statistics for C:/Drive.

        Returns:
            Dict with storage stats
        """
        import shutil

        stats = {}

        try:
            # Total, used, free space
            total, used, free = shutil.disk_usage(cls.DRIVE_ROOT)
            stats['total_gb'] = total / (1024**3)
            stats['used_gb'] = used / (1024**3)
            stats['free_gb'] = free / (1024**3)
            stats['used_percent'] = (used / total) * 100

            # Count items in key directories
            if cls.MODELS_DIR.exists():
                stats['models_count'] = len(list(cls.MODELS_DIR.rglob('*')))

            if cls.DATA_DIR.exists():
                stats['data_files_count'] = len(list(cls.DATA_DIR.rglob('*')))

            if cls.BRAIN_DB.exists():
                stats['brain_db_size_mb'] = cls.BRAIN_DB.stat().st_size / (1024**2)

        except Exception as e:
            stats['error'] = str(e)

        return stats

    @classmethod
    def get_platform_info(cls) -> Dict[str, any]:
        """
        Get platform information for debugging and compatibility.

        Returns:
            Dict with platform details
        """
        return {
            'system': platform.system(),
            'system_name': {
                'Windows': 'Windows',
                'Darwin': 'macOS',
                'Linux': 'Linux'
            }.get(platform.system(), 'Unknown'),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'alfred_root': str(cls.DRIVE_ROOT),
            'alfred_home_override': os.getenv('ALFRED_HOME'),
            'is_windows': platform.system() == 'Windows',
            'is_macos': platform.system() == 'Darwin',
            'is_linux': platform.system() == 'Linux'
        }

    @classmethod
    def print_structure(cls):
        """Print the complete directory structure."""
        # Get platform info
        platform_info = cls.get_platform_info()

        print("\n" + "="*60)
        print("Alfred AI Assistant - Directory Structure")
        print("="*60)
        print(f"\nPlatform: {platform_info['system_name']} ({platform_info['system']})")
        print(f"Python:   {platform_info['python_version']}")
        print(f"Root:     {cls.DRIVE_ROOT}")
        if platform_info['alfred_home_override']:
            print(f"Override: {platform_info['alfred_home_override']}")
        print(f"\nModels:")
        print(f"  Ollama:     {cls.OLLAMA_MODELS_DIR}")
        print(f"  Voice:      {cls.VOICE_MODELS_DIR}")
        print(f"  Vision:     {cls.VISION_MODELS_DIR}")
        print(f"  Embeddings: {cls.EMBEDDINGS_MODELS_DIR}")
        print(f"\nData:")
        print(f"  Brain DB:       {cls.BRAIN_DB}")
        print(f"  Vector Store:   {cls.VECTOR_STORE_DIR}")
        print(f"  Cache:          {cls.CACHE_DIR}")
        print(f"\nConfiguration:")
        print(f"  Config Dir:  {cls.CONFIG_DIR}")
        print(f"  Alfred:      {cls.ALFRED_CONFIG}")
        print(f"  Models:      {cls.MODELS_CONFIG}")
        print(f"\nLogs:")
        print(f"  Alfred:       {cls.ALFRED_LOGS_DIR}")
        print(f"  Integrations: {cls.INTEGRATIONS_LOGS_DIR}")
        print(f"  Errors:       {cls.ERRORS_LOGS_DIR}")
        print(f"\nBackups:")
        print(f"  Daily:  {cls.DAILY_BACKUPS_DIR}")
        print(f"  Weekly: {cls.WEEKLY_BACKUPS_DIR}")
        print("="*60 + "\n")


if __name__ == "__main__":
    # Test PathManager
    print("Testing PathManager...")

    # Verify access
    if PathManager.verify_drive_access():
        print("[OK] C:/Drive is accessible")
    else:
        print("[FAIL] C:/Drive is not accessible")
        exit(1)

    # Ensure all paths
    print("\nCreating directory structure...")
    results = PathManager.ensure_all_paths()
    success_count = sum(1 for v in results.values() if v)
    print(f"[OK] Created {success_count}/{len(results)} directories")

    # Show structure
    PathManager.print_structure()

    # Show stats
    stats = PathManager.get_stats()
    print(f"Storage Stats:")
    print(f"  Total: {stats.get('total_gb', 0):.2f} GB")
    print(f"  Used:  {stats.get('used_gb', 0):.2f} GB ({stats.get('used_percent', 0):.1f}%)")
    print(f"  Free:  {stats.get('free_gb', 0):.2f} GB")
