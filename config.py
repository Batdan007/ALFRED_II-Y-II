"""
ALFRED_UBX Configuration Module
Handles all configuration, API keys, and settings management.

Author: Daniel J. Rita aka BATDAN007
https://github.com/Batdan007/ALFRED_UBX
"""

import os
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from enum import Enum

# Try to import dotenv, but don't fail if not available
try:
    from dotenv import load_dotenv, set_key
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class AIProvider(str, Enum):
    """Supported AI providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GROQ = "groq"


@dataclass
class APIKeys:
    """API key storage."""
    anthropic: str = ""
    openai: str = ""
    groq: str = ""
    
    def get_active_providers(self) -> List[str]:
        """Return list of providers with valid keys."""
        providers = []
        if self.anthropic and self.anthropic != "your_anthropic_key_here":
            providers.append("anthropic")
        if self.openai and self.openai != "your_openai_key_here":
            providers.append("openai")
        if self.groq and self.groq != "your_groq_key_here":
            providers.append("groq")
        return providers
    
    def has_any_key(self) -> bool:
        """Check if at least one valid API key is set."""
        return len(self.get_active_providers()) > 0


@dataclass
class MemorySettings:
    """Memory system settings."""
    enabled: bool = True
    path: str = "./memory"
    max_conversations: int = 1000
    auto_save: bool = True
    save_interval: int = 300  # seconds


@dataclass
class ServerSettings:
    """Web server settings."""
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False
    workers: int = 1


@dataclass
class ModelSettings:
    """AI model settings."""
    default_provider: str = "anthropic"
    anthropic_model: str = "claude-sonnet-4-20250514"
    openai_model: str = "gpt-4o"
    groq_model: str = "llama-3.3-70b-versatile"
    max_tokens: int = 4096
    temperature: float = 0.7


@dataclass
class VoiceSettings:
    """Text-to-speech settings."""
    enabled: bool = True
    rate: int = 150
    volume: float = 1.0
    voice_id: Optional[str] = None


@dataclass
class Config:
    """Main configuration class."""
    api_keys: APIKeys = field(default_factory=APIKeys)
    memory: MemorySettings = field(default_factory=MemorySettings)
    server: ServerSettings = field(default_factory=ServerSettings)
    model: ModelSettings = field(default_factory=ModelSettings)
    voice: VoiceSettings = field(default_factory=VoiceSettings)
    debug: bool = False
    
    # File paths
    _config_file: str = field(default="config.json", repr=False)
    _env_file: str = field(default=".env", repr=False)
    
    def __post_init__(self):
        """Load configuration after initialization."""
        self._load_from_env()
        self._load_from_file()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        if DOTENV_AVAILABLE:
            env_path = Path(self._env_file)
            if env_path.exists():
                load_dotenv(env_path)
        
        # API Keys
        self.api_keys.anthropic = os.getenv("ANTHROPIC_API_KEY", self.api_keys.anthropic)
        self.api_keys.openai = os.getenv("OPENAI_API_KEY", self.api_keys.openai)
        self.api_keys.groq = os.getenv("GROQ_API_KEY", self.api_keys.groq)
        
        # Model settings
        self.model.default_provider = os.getenv("DEFAULT_PROVIDER", self.model.default_provider)
        self.model.anthropic_model = os.getenv("ANTHROPIC_MODEL", self.model.anthropic_model)
        self.model.openai_model = os.getenv("OPENAI_MODEL", self.model.openai_model)
        self.model.groq_model = os.getenv("GROQ_MODEL", self.model.groq_model)
        
        # Server settings
        self.server.host = os.getenv("HOST", self.server.host)
        self.server.port = int(os.getenv("PORT", self.server.port))
        
        # Memory settings
        self.memory.enabled = os.getenv("MEMORY_ENABLED", "true").lower() == "true"
        self.memory.path = os.getenv("MEMORY_PATH", self.memory.path)
        
        # Debug
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
    
    def _load_from_file(self):
        """Load configuration from JSON file."""
        config_path = Path(self._config_file)
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                self._update_from_dict(data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")
    
    def _update_from_dict(self, data: Dict[str, Any]):
        """Update configuration from dictionary."""
        if "api_keys" in data:
            for key, value in data["api_keys"].items():
                if hasattr(self.api_keys, key):
                    setattr(self.api_keys, key, value)
        
        if "memory" in data:
            for key, value in data["memory"].items():
                if hasattr(self.memory, key):
                    setattr(self.memory, key, value)
        
        if "server" in data:
            for key, value in data["server"].items():
                if hasattr(self.server, key):
                    setattr(self.server, key, value)
        
        if "model" in data:
            for key, value in data["model"].items():
                if hasattr(self.model, key):
                    setattr(self.model, key, value)
        
        if "voice" in data:
            for key, value in data["voice"].items():
                if hasattr(self.voice, key):
                    setattr(self.voice, key, value)
        
        if "debug" in data:
            self.debug = data["debug"]
    
    def save_to_file(self, path: Optional[str] = None):
        """Save configuration to JSON file."""
        config_path = Path(path or self._config_file)
        data = {
            "api_keys": asdict(self.api_keys),
            "memory": asdict(self.memory),
            "server": asdict(self.server),
            "model": asdict(self.model),
            "voice": asdict(self.voice),
            "debug": self.debug,
        }
        
        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def save_to_env(self, path: Optional[str] = None):
        """Save API keys to .env file."""
        env_path = Path(path or self._env_file)
        
        env_content = f"""# ALFRED_UBX Configuration
# Generated by config.py

# AI Provider API Keys
ANTHROPIC_API_KEY={self.api_keys.anthropic}
OPENAI_API_KEY={self.api_keys.openai}
GROQ_API_KEY={self.api_keys.groq}

# Default Provider
DEFAULT_PROVIDER={self.model.default_provider}

# Model Settings
ANTHROPIC_MODEL={self.model.anthropic_model}
OPENAI_MODEL={self.model.openai_model}
GROQ_MODEL={self.model.groq_model}

# Memory Settings
MEMORY_ENABLED={str(self.memory.enabled).lower()}
MEMORY_PATH={self.memory.path}

# Server Settings
HOST={self.server.host}
PORT={self.server.port}

# Debug
DEBUG={str(self.debug).lower()}
"""
        
        with open(env_path, "w") as f:
            f.write(env_content)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "api_keys": asdict(self.api_keys),
            "memory": asdict(self.memory),
            "server": asdict(self.server),
            "model": asdict(self.model),
            "voice": asdict(self.voice),
            "debug": self.debug,
        }


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """Reload configuration from files."""
    global _config
    _config = Config()
    return _config


# Quick access functions
def get_api_key(provider: str) -> str:
    """Get API key for a specific provider."""
    config = get_config()
    return getattr(config.api_keys, provider, "")


def get_default_provider() -> str:
    """Get the default AI provider."""
    config = get_config()
    
    # If default provider has a key, use it
    default = config.model.default_provider
    if getattr(config.api_keys, default, ""):
        return default
    
    # Otherwise, use first available provider
    active = config.api_keys.get_active_providers()
    if active:
        return active[0]
    
    return "anthropic"  # Fallback


if __name__ == "__main__":
    # Test configuration
    config = get_config()
    print("Configuration loaded:")
    print(f"  Active providers: {config.api_keys.get_active_providers()}")
    print(f"  Default provider: {get_default_provider()}")
    print(f"  Memory enabled: {config.memory.enabled}")
    print(f"  Server: {config.server.host}:{config.server.port}")
