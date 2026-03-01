"""
Base language configuration class.

Defines all required keys for language-specific strings and patterns.
"""

from typing import Dict, List


class LanguageConfig:
    """Base class for language-specific configuration."""

    # Comps page labels
    avg_place: str
    pick_rate: str
    win_rate: str
    top_4_rate: str

    # Units page labels
    ability_label: str
    stats_label: str

    # Unit stats labels
    health: str
    mana: str
    attack_damage: str
    ability_power: str
    armor: str
    magic_resist: str
    attack_speed: str
    crit_chance: str
    crit_damage: str
    range: str

    # Ability description markers
    passive_marker: str
    active_marker: str
    unlock_marker: str

    # Traits list (for unit type classification)
    traits: List[str]

    # Unit types (for type classification)
    unit_types: List[str]

    # Items page labels
    tft_item_stats: str
    item_stats_labels: List[str]  # Vietnamese equivalents

    # Augments page keywords
    navigation_keywords: List[str]
    footer_keywords: List[str]

    def __init__(self):
        """Initialize with default values - must be overridden in subclasses."""
        raise NotImplementedError(
            "LanguageConfig is an abstract base class. "
            "Use a concrete implementation like EnglishConfig or VietnameseConfig."
        )
