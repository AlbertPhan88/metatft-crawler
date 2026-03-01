"""
Language configuration module for MetaTFT Crawler.

Provides language-specific strings and patterns for all supported languages.
"""

from .base import LanguageConfig
from .loader import get_language_config

__all__ = ["LanguageConfig", "get_language_config"]
