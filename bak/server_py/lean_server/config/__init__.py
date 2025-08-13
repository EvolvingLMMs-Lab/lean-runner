"""
This package handles the configuration management for the Lean server.

It exports the main Config class and the get_config function for easy access.
"""

from .config import Config, get_config

__all__ = ["Config", "get_config"]
