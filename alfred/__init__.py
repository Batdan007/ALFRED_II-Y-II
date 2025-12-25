"""
Alfred - 100% Local AI Assistant with Permanent Memory
Patent-Pending 11-Table Memory Architecture

Simple Python API for integrating Alfred into your projects.

Example:
    from alfred import Alfred

    bot = Alfred()
    response = bot.respond("Hello Alfred!")
    print(response)

Features:
- 100% local AI (no API key needed)
- Permanent memory (remembers everything)
- Privacy-first (no cloud, no data sharing)
- Auto-starts Ollama server

Author: Daniel J Rita (BATDAN)
Version: 3.0.0-ultimate
"""

from alfred.client import Alfred

__version__ = "3.0.0-ultimate"
__author__ = "Daniel J Rita (BATDAN)"
__all__ = ["Alfred"]
