"""
Tests for language configuration system.
"""

import pytest
from src.metatft_crawler.languages.loader import (
    get_language_config,
    get_supported_languages,
)
from src.metatft_crawler.languages.en import EnglishConfig
from src.metatft_crawler.languages.vi import VietnameseConfig


class TestLanguageLoader:
    """Test language configuration loader."""

    def test_get_supported_languages(self):
        """Test that supported languages are returned correctly."""
        langs = get_supported_languages()
        assert "en" in langs
        assert "vi" in langs
        assert len(langs) >= 2

    def test_get_english_config(self):
        """Test getting English configuration."""
        config = get_language_config("en")
        assert isinstance(config, EnglishConfig)
        assert config.avg_place == "Avg Place"
        assert config.pick_rate == "Pick Rate"
        assert config.win_rate == "Win Rate"
        assert config.top_4_rate == "Top 4 Rate"

    def test_get_vietnamese_config(self):
        """Test getting Vietnamese configuration."""
        config = get_language_config("vi")
        assert isinstance(config, VietnameseConfig)
        assert config.avg_place == "Hạng TB"
        assert config.pick_rate == "Tỷ Lệ Chọn"
        assert config.win_rate == "Tỷ Lệ Thắng"
        assert config.top_4_rate == "Tỷ Lệ Top 4"

    def test_language_config_caching(self):
        """Test that language configs are cached."""
        config1 = get_language_config("en")
        config2 = get_language_config("en")
        assert config1 is config2

    def test_unsupported_language_raises_error(self):
        """Test that unsupported languages raise ValueError."""
        with pytest.raises(ValueError) as excinfo:
            get_language_config("unsupported")
        assert "unsupported" in str(excinfo.value).lower()
        assert "supported languages" in str(excinfo.value).lower()

    def test_case_insensitive_language_code(self):
        """Test that language codes are case-insensitive."""
        config1 = get_language_config("EN")
        config2 = get_language_config("en")
        config3 = get_language_config("En")
        assert config1 is config2
        assert config2 is config3

    def test_english_config_has_all_required_attributes(self):
        """Test that English config has all required attributes."""
        config = get_language_config("en")
        # Comps stats
        assert hasattr(config, "avg_place")
        assert hasattr(config, "pick_rate")
        assert hasattr(config, "win_rate")
        assert hasattr(config, "top_4_rate")
        # Unit tabs
        assert hasattr(config, "ability_label")
        assert hasattr(config, "stats_label")
        # Unit stats
        assert hasattr(config, "health")
        assert hasattr(config, "mana")
        assert hasattr(config, "attack_damage")
        assert hasattr(config, "ability_power")
        assert hasattr(config, "armor")
        assert hasattr(config, "magic_resist")
        assert hasattr(config, "attack_speed")
        assert hasattr(config, "crit_chance")
        assert hasattr(config, "crit_damage")
        assert hasattr(config, "range")
        # Ability markers
        assert hasattr(config, "passive_marker")
        assert hasattr(config, "active_marker")
        assert hasattr(config, "unlock_marker")
        # Lists
        assert hasattr(config, "traits")
        assert hasattr(config, "unit_types")
        # Items
        assert hasattr(config, "tft_item_stats")
        assert hasattr(config, "item_stats_labels")
        # Augments
        assert hasattr(config, "navigation_keywords")
        assert hasattr(config, "footer_keywords")

    def test_vietnamese_config_has_all_required_attributes(self):
        """Test that Vietnamese config has all required attributes."""
        config = get_language_config("vi")
        # Same attributes as English
        assert hasattr(config, "avg_place")
        assert hasattr(config, "pick_rate")
        assert hasattr(config, "win_rate")
        assert hasattr(config, "top_4_rate")
        assert hasattr(config, "ability_label")
        assert hasattr(config, "stats_label")
        assert hasattr(config, "traits")
        assert hasattr(config, "unit_types")
        assert hasattr(config, "tft_item_stats")
        assert hasattr(config, "navigation_keywords")

    def test_traits_list_not_empty(self):
        """Test that traits list is not empty."""
        en_config = get_language_config("en")
        vi_config = get_language_config("vi")
        assert len(en_config.traits) > 0
        assert len(vi_config.traits) > 0
        # Both should have the same trait names (game terms)
        assert set(en_config.traits) == set(vi_config.traits)

    def test_unit_types_list_not_empty(self):
        """Test that unit types list is not empty."""
        en_config = get_language_config("en")
        vi_config = get_language_config("vi")
        assert len(en_config.unit_types) > 0
        assert len(vi_config.unit_types) > 0
        # Both should have the same unit types (game terms)
        assert en_config.unit_types == vi_config.unit_types

    def test_navigation_keywords_not_empty(self):
        """Test that navigation keywords are present."""
        config = get_language_config("en")
        assert len(config.navigation_keywords) > 0
        assert "MetaTFT" in config.navigation_keywords or "Comps" in config.navigation_keywords

    def test_footer_keywords_not_empty(self):
        """Test that footer keywords are present."""
        config = get_language_config("en")
        assert len(config.footer_keywords) > 0
        assert "Privacy" in config.footer_keywords or "GitHub" in config.footer_keywords


class TestEnglishConfig:
    """Test English configuration."""

    def test_english_comps_stats_labels(self):
        """Test English comps stats labels."""
        config = EnglishConfig()
        assert config.avg_place == "Avg Place"
        assert config.pick_rate == "Pick Rate"
        assert config.win_rate == "Win Rate"
        assert config.top_4_rate == "Top 4 Rate"

    def test_english_unit_stats_labels(self):
        """Test English unit stats labels."""
        config = EnglishConfig()
        assert config.health == "Health"
        assert config.mana == "Mana"
        assert config.attack_damage == "Attack Damage"
        assert config.ability_power == "Ability Power"
        assert config.armor == "Armor"
        assert config.magic_resist == "Magic Resist"
        assert config.attack_speed == "Attack Speed"
        assert config.crit_chance == "Crit Chance"
        assert config.crit_damage == "Crit Damage"
        assert config.range == "Range"

    def test_english_ability_markers(self):
        """Test English ability markers."""
        config = EnglishConfig()
        assert config.passive_marker == "Passive:"
        assert config.active_marker == "Active:"
        assert config.unlock_marker == "Unlock:"

    def test_english_known_traits(self):
        """Test that known traits are defined."""
        config = EnglishConfig()
        expected_traits = [
            "Attack",
            "Fighter",
            "Void",
            "Riftscourge",
            "Magic",
            "Marksman",
            "Zaun",
            "Zaunite",
            "Yordle",
            "Longshot",
            "Duelist",
            "Visionary",
            "Knight",
            "Assassin",
            "Mage",
            "Ranger",
            "Support",
            "Tank",
            "Bruiser",
            "Shurima",
            "Noxus",
            "Piltover",
            "Demacia",
            "Ionia",
            "Shadow",
            "Star",
            "Caretaker",
            "Chemtech",
            "Corrupt",
            "Enforcer",
        ]
        for trait in expected_traits:
            assert trait in config.traits


class TestVietnameseConfig:
    """Test Vietnamese configuration."""

    def test_vietnamese_comps_stats_labels(self):
        """Test Vietnamese comps stats labels."""
        config = VietnameseConfig()
        assert config.avg_place == "Hạng TB"
        assert config.pick_rate == "Tỷ Lệ Chọn"
        assert config.win_rate == "Tỷ Lệ Thắng"
        assert config.top_4_rate == "Tỷ Lệ Top 4"

    def test_vietnamese_item_stats_labels(self):
        """Test Vietnamese item stats labels."""
        config = VietnameseConfig()
        assert config.tft_item_stats == "Số Liệu Trang Bị"
        assert len(config.item_stats_labels) > 0
        assert "Số Liệu Trang Bị" in config.item_stats_labels

    def test_vietnamese_traits_same_as_english(self):
        """Test that Vietnamese traits are same as English (game terms)."""
        en_config = EnglishConfig()
        vi_config = VietnameseConfig()
        assert set(en_config.traits) == set(vi_config.traits)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
