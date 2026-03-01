"""
Language configuration loader.

Maps language codes to appropriate configuration classes and caches them.
"""

from typing import Dict
from .base import LanguageConfig
from .en import EnglishConfig
from .vi import VietnameseConfig


# Cache for loaded language configs
_config_cache: Dict[str, LanguageConfig] = {}


def get_language_config(language: str) -> LanguageConfig:
    """
    Get the language configuration for the specified language code.

    Args:
        language: Language code ('en' for English, 'vi' for Vietnamese)

    Returns:
        LanguageConfig instance for the specified language

    Raises:
        ValueError: If the language code is not supported
    """
    # Normalize to lowercase
    language = language.lower().strip()

    # Check cache first
    if language in _config_cache:
        return _config_cache[language]

    # Map language codes to configuration classes
    language_map = {
        "en": EnglishConfig,
        "vi": VietnameseConfig,
    }

    if language not in language_map:
        supported = ", ".join(sorted(language_map.keys()))
        raise ValueError(
            f"Unsupported language: '{language}'. "
            f"Supported languages: {supported}"
        )

    # Create and cache the configuration
    config = language_map[language]()
    _config_cache[language] = config
    return config


def get_supported_languages() -> list:
    """Get a list of supported language codes."""
    return ["en", "vi"]
