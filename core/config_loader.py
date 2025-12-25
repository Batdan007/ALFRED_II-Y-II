"""
Configuration Loader - YAML-based configuration management

Loads configuration from C:/Drive/config/ directory.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from .path_manager import PathManager


class ConfigLoader:
    """
    YAML-based configuration loader for Alfred AI Assistant.

    Loads from C:/Drive/config/ by default.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize ConfigLoader

        Args:
            config_dir: Directory containing config files (default: C:/Drive/config)
        """
        self.config_dir = config_dir or PathManager.CONFIG_DIR
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load environment variables
        env_file = self.config_dir / ".env"
        if env_file.exists():
            load_dotenv(env_file)

        # Configuration cache
        self._configs = {}

    def load(self, config_name: str) -> Dict[str, Any]:
        """
        Load a configuration file.

        Args:
            config_name: Name of config file (without .yaml extension)

        Returns:
            Configuration dictionary
        """
        # Check cache
        if config_name in self._configs:
            return self._configs[config_name]

        # Load from file
        config_file = self.config_dir / f"{config_name}.yaml"

        if not config_file.exists():
            # Return empty config if file doesn't exist
            return {}

        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f) or {}
                self._configs[config_name] = config
                return config
        except Exception as e:
            print(f"Warning: Failed to load {config_file}: {e}")
            return {}

    def save(self, config_name: str, config: Dict[str, Any]):
        """
        Save a configuration file.

        Args:
            config_name: Name of config file (without .yaml extension)
            config: Configuration dictionary to save
        """
        config_file = self.config_dir / f"{config_name}.yaml"

        try:
            with open(config_file, 'w') as f:
                yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
                self._configs[config_name] = config
        except Exception as e:
            print(f"Error: Failed to save {config_file}: {e}")

    def get(self, config_name: str, key: str, default: Any = None) -> Any:
        """
        Get a specific configuration value.

        Args:
            config_name: Name of config file
            key: Configuration key (supports dot notation: "section.subsection.key")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        config = self.load(config_name)

        # Support dot notation for nested keys
        keys = key.split('.')
        value = config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, config_name: str, key: str, value: Any):
        """
        Set a specific configuration value.

        Args:
            config_name: Name of config file
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        config = self.load(config_name)

        # Support dot notation for nested keys
        keys = key.split('.')
        current = config

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        self.save(config_name, config)

    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)

    def create_default_configs(self):
        """Create default configuration files if they don't exist."""

        # Alfred main configuration
        if not (self.config_dir / "alfred.yaml").exists():
            alfred_config = {
                'brain': {
                    'database_path': str(PathManager.BRAIN_DB),
                    'cache_size': 1000,
                    'auto_backup': True,
                    'backup_interval': 'daily',
                },
                'logging': {
                    'level': 'INFO',
                    'log_to_file': True,
                    'log_dir': str(PathManager.ALFRED_LOGS_DIR),
                },
                'features': {
                    'voice_enabled': False,
                    'vision_enabled': False,
                    'rag_enabled': False,
                },
            }
            self.save('alfred', alfred_config)

        # Models configuration
        if not (self.config_dir / "models.yaml").exists():
            models_config = {
                'ollama': {
                    'enabled': True,
                    'api_base': 'http://localhost:11434',
                    'primary_model': 'dolphin-mixtral:8x7b',
                    'fallback_model': 'llama3.3:70b',
                    'fast_model': 'dolphin-llama3:8b',
                },
                'claude': {
                    'enabled': False,
                    'api_key_env': 'ANTHROPIC_API_KEY',
                    'model': 'claude-3-5-sonnet-20241022',
                },
                'openai': {
                    'enabled': False,
                    'api_key_env': 'OPENAI_API_KEY',
                    'model': 'gpt-4-turbo-preview',
                },
                'groq': {
                    'enabled': False,
                    'api_key_env': 'GROQ_API_KEY',
                    'model': 'mixtral-8x7b-32768',
                },
                'voice': {
                    'tts_model': 'parler-tts',
                    'tts_model_path': str(PathManager.VOICE_MODELS_DIR / 'parler-tts'),
                    'stt_model': 'whisper-large-v3',
                    'stt_model_path': str(PathManager.VOICE_MODELS_DIR / 'whisper-large-v3'),
                    'wake_word': 'alfred',
                },
                'vision': {
                    'camera_index': 0,
                    'resolution': [1920, 1080],
                    'analyzer': 'gpt-4-vision',
                },
            }
            self.save('models', models_config)

        # Integrations configuration
        if not (self.config_dir / "integrations.yaml").exists():
            integrations_config = {
                'rag': {
                    'enabled': False,
                    'vector_store': 'chromadb',
                    'vector_store_path': str(PathManager.VECTOR_STORE_DIR),
                    'embedding_model': 'all-MiniLM-L6-v2',
                    'chunk_size': 1000,
                    'chunk_overlap': 200,
                },
                'fabric': {
                    'enabled': False,
                    'patterns_dir': str(PathManager.FABRIC_PATTERNS_DIR),
                },
            }
            self.save('integrations', integrations_config)

        # Paths configuration (for reference)
        if not (self.config_dir / "paths.yaml").exists():
            paths_config = {
                'drive_root': str(PathManager.DRIVE_ROOT),
                'models_dir': str(PathManager.MODELS_DIR),
                'data_dir': str(PathManager.DATA_DIR),
                'config_dir': str(PathManager.CONFIG_DIR),
                'logs_dir': str(PathManager.LOGS_DIR),
                'backups_dir': str(PathManager.BACKUPS_DIR),
            }
            self.save('paths', paths_config)

    def list_configs(self) -> list:
        """
        List all available configuration files.

        Returns:
            List of config file names (without .yaml extension)
        """
        config_files = list(self.config_dir.glob("*.yaml"))
        return [f.stem for f in config_files]


if __name__ == "__main__":
    # Test ConfigLoader
    print("Testing ConfigLoader...")

    loader = ConfigLoader()
    print(f"[OK] ConfigLoader initialized: {loader.config_dir}")

    # Create default configs
    print("\nCreating default configurations...")
    loader.create_default_configs()
    print("[OK] Default configs created")

    # List configs
    configs = loader.list_configs()
    print(f"\nAvailable configs: {configs}")

    # Test loading
    alfred_config = loader.load('alfred')
    print(f"\nAlfred config loaded:")
    print(f"  Brain DB: {alfred_config.get('brain', {}).get('database_path')}")
    print(f"  Log level: {alfred_config.get('logging', {}).get('level')}")

    # Test get with dot notation
    db_path = loader.get('alfred', 'brain.database_path')
    print(f"\nUsing dot notation: {db_path}")

    # Test environment variables
    test_key = loader.get_env('ANTHROPIC_API_KEY', 'not-set')
    print(f"Environment test: ANTHROPIC_API_KEY = {test_key[:20] if test_key != 'not-set' else 'not-set'}...")
