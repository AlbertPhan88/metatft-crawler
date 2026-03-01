#!/usr/bin/env python3
"""
Manual test script for language configuration system.
No dependencies on pytest - runs standalone.
"""

import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metatft_crawler.languages.loader import (
    get_language_config,
    get_supported_languages,
)
from src.metatft_crawler.languages.en import EnglishConfig
from src.metatft_crawler.languages.vi import VietnameseConfig


def test_language_loader():
    """Test language configuration loader."""
    print("Testing Language Loader...")

    # Test supported languages
    langs = get_supported_languages()
    assert "en" in langs, "English should be supported"
    assert "vi" in langs, "Vietnamese should be supported"
    print("  ✓ Supported languages correct")

    # Test English config
    en_config = get_language_config("en")
    assert isinstance(en_config, EnglishConfig), "Should return EnglishConfig"
    assert en_config.avg_place == "Avg Place", "English avg_place incorrect"
    assert en_config.pick_rate == "Pick Rate", "English pick_rate incorrect"
    assert en_config.win_rate == "Win Rate", "English win_rate incorrect"
    assert en_config.top_4_rate == "Top 4 Rate", "English top_4_rate incorrect"
    print("  ✓ English configuration correct")

    # Test Vietnamese config
    vi_config = get_language_config("vi")
    assert isinstance(vi_config, VietnameseConfig), "Should return VietnameseConfig"
    assert vi_config.avg_place == "Hạng TB", "Vietnamese avg_place incorrect"
    assert vi_config.pick_rate == "Tỷ Lệ Chọn", "Vietnamese pick_rate incorrect"
    assert vi_config.win_rate == "Tỷ Lệ Thắng", "Vietnamese win_rate incorrect"
    assert vi_config.top_4_rate == "Tỷ Lệ Top 4", "Vietnamese top_4_rate incorrect"
    print("  ✓ Vietnamese configuration correct")

    # Test caching
    en_config2 = get_language_config("en")
    assert en_config is en_config2, "Caching should return same instance"
    print("  ✓ Language config caching works")

    # Test case insensitivity
    en_upper = get_language_config("EN")
    en_mixed = get_language_config("En")
    assert en_upper is en_config, "Case insensitivity should work"
    assert en_mixed is en_config, "Case insensitivity should work"
    print("  ✓ Case-insensitive language codes work")

    # Test error handling
    try:
        get_language_config("unsupported")
        assert False, "Should raise ValueError for unsupported language"
    except ValueError as e:
        assert "unsupported" in str(e).lower(), "Error message should mention unsupported"
        print("  ✓ Error handling for unsupported languages works")


def test_english_config_attributes():
    """Test that English config has all required attributes."""
    print("\nTesting English Config Attributes...")
    config = get_language_config("en")

    # Test all required attributes exist
    required_attrs = [
        "avg_place",
        "pick_rate",
        "win_rate",
        "top_4_rate",
        "ability_label",
        "stats_label",
        "health",
        "mana",
        "attack_damage",
        "ability_power",
        "armor",
        "magic_resist",
        "attack_speed",
        "crit_chance",
        "crit_damage",
        "range",
        "passive_marker",
        "active_marker",
        "unlock_marker",
        "traits",
        "unit_types",
        "tft_item_stats",
        "item_stats_labels",
        "navigation_keywords",
        "footer_keywords",
    ]

    for attr in required_attrs:
        assert hasattr(config, attr), f"Missing attribute: {attr}"
    print(f"  ✓ All {len(required_attrs)} required attributes present")

    # Test list attributes are not empty
    assert len(config.traits) > 0, "Traits list should not be empty"
    assert len(config.unit_types) > 0, "Unit types list should not be empty"
    assert len(config.navigation_keywords) > 0, "Navigation keywords should not be empty"
    assert len(config.footer_keywords) > 0, "Footer keywords should not be empty"
    print("  ✓ All list attributes are non-empty")


def test_vietnamese_config_attributes():
    """Test that Vietnamese config has all required attributes."""
    print("\nTesting Vietnamese Config Attributes...")
    config = get_language_config("vi")

    # Test Vietnamese-specific attributes
    assert config.tft_item_stats == "Số Liệu Trang Bị", "Vietnamese item stats label incorrect"
    assert len(config.item_stats_labels) > 0, "Vietnamese item stats labels should exist"
    assert "Số Liệu Trang Bị" in config.item_stats_labels, "Primary label should be in alternate labels"
    print("  ✓ Vietnamese-specific attributes correct")

    # Test traits - Vietnamese has both English and Vietnamese versions for page matching
    en_config = get_language_config("en")
    # English traits should be a subset of Vietnamese traits (Vietnamese has both versions)
    assert set(en_config.traits).issubset(set(config.traits)), "English traits should be subset of Vietnamese"
    # Vietnamese should have more traits (both English and Vietnamese versions)
    assert len(config.traits) > len(en_config.traits), "Vietnamese should have both EN and VI trait names"
    # Same for unit types
    assert set(en_config.unit_types).issubset(set(config.unit_types)), "English unit types should be subset of Vietnamese"
    print("  ✓ Game terms are consistent across languages")


def test_module_exports():
    """Test that module exports are correct."""
    print("\nTesting Module Exports...")

    # Test that main module exports language utilities
    from src.metatft_crawler import get_language_config as exported_get_config
    from src.metatft_crawler import get_supported_languages as exported_get_langs

    # Verify they work
    langs = exported_get_langs()
    assert "en" in langs, "Exported get_supported_languages should work"
    config = exported_get_config("en")
    assert config is not None, "Exported get_language_config should work"
    print("  ✓ Module exports language utilities correctly")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Language Configuration System - Test Suite")
    print("=" * 60)

    try:
        test_language_loader()
        test_english_config_attributes()
        test_vietnamese_config_attributes()
        test_module_exports()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
