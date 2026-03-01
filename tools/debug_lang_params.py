#!/usr/bin/env python3
"""
Debug script to check if language config parameters are being passed correctly to JavaScript.
"""

import asyncio
import sys
import os
from playwright.async_api import async_playwright

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metatft_crawler.languages.loader import get_language_config


async def debug_params():
    """Check if parameters are passed correctly to JavaScript."""

    print("=" * 80)
    print("DEBUG: Language Config Parameter Passing")
    print("=" * 80)

    # Get language configs
    en_config = get_language_config("en")
    vi_config = get_language_config("vi")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Navigate to a unit page
        print("\nNavigating to Baron Nashor page...")
        await page.goto(
            "https://www.metatft.com/units/BaronNashor",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        await page.wait_for_timeout(2000)

        # Test with English config
        print("\n[TEST 1] English config parameters:")
        print(f"  traits type: {type(en_config.traits).__name__}")
        print(f"  traits: {en_config.traits}")
        print(f"  unit_types: {en_config.unit_types}")

        en_result = await page.evaluate(
            """
            (langConfig) => {
                return {
                    received_properties: Object.keys(langConfig),
                    traits_type: typeof langConfig.traits,
                    traits_is_array: Array.isArray(langConfig.traits),
                    traits_length: langConfig.traits ? langConfig.traits.length : null,
                    traits_first: langConfig.traits ? langConfig.traits[0] : null,
                    unit_types: langConfig.unit_types,
                    ability_label: langConfig.ability_label,
                    stats_label: langConfig.stats_label,
                };
            }
            """,
            {
                "traits": en_config.traits,
                "unit_types": en_config.unit_types,
                "ability_label": en_config.ability_label,
                "stats_label": en_config.stats_label,
            },
        )

        print(f"\n✅ English config received in JavaScript:")
        print(f"  Properties: {en_result['received_properties']}")
        print(f"  traits type: {en_result['traits_type']}")
        print(f"  traits is array: {en_result['traits_is_array']}")
        print(f"  traits length: {en_result['traits_length']}")
        print(f"  traits[0]: {en_result['traits_first']}")
        print(f"  unit_types: {en_result['unit_types']}")
        print(f"  ability_label: {en_result['ability_label']}")
        print(f"  stats_label: {en_result['stats_label']}")

        # Test with Vietnamese config
        print("\n[TEST 2] Vietnamese config parameters:")
        print(f"  traits type: {type(vi_config.traits).__name__}")
        print(f"  unit_types: {vi_config.unit_types}")
        print(f"  tft_item_stats: {vi_config.tft_item_stats}")

        vi_result = await page.evaluate(
            """
            (langConfig) => {
                return {
                    received_properties: Object.keys(langConfig),
                    traits_type: typeof langConfig.traits,
                    traits_is_array: Array.isArray(langConfig.traits),
                    traits_length: langConfig.traits ? langConfig.traits.length : null,
                    traits_first: langConfig.traits ? langConfig.traits[0] : null,
                    unit_types: langConfig.unit_types,
                    tft_item_stats: langConfig.tft_item_stats,
                };
            }
            """,
            {
                "traits": vi_config.traits,
                "unit_types": vi_config.unit_types,
                "tft_item_stats": vi_config.tft_item_stats,
            },
        )

        print(f"\n✅ Vietnamese config received in JavaScript:")
        print(f"  Properties: {vi_result['received_properties']}")
        print(f"  traits type: {vi_result['traits_type']}")
        print(f"  traits is array: {vi_result['traits_is_array']}")
        print(f"  traits length: {vi_result['traits_length']}")
        print(f"  traits[0]: {vi_result['traits_first']}")
        print(f"  unit_types: {vi_result['unit_types']}")
        print(f"  tft_item_stats: {vi_result['tft_item_stats']}")

        # Test actual extraction logic
        print("\n[TEST 3] Testing extraction with config parameters:")

        # English extraction test
        en_extract = await page.evaluate(
            """
            (langConfig) => {
                const pageText = document.body.innerText;
                const lines = pageText.split('\\n').map(l => l.trim()).filter(l => l && l.length > 0);

                console.log('Looking for ability tab: ' + langConfig.ability_label);
                console.log('Looking for stats tab: ' + langConfig.stats_label);
                console.log('Total lines:', lines.length);

                let abilityTabIndex = -1;
                for (let i = 0; i < Math.min(100, lines.length); i++) {
                    if (lines[i] === langConfig.ability_label && lines[i+1] === langConfig.stats_label) {
                        abilityTabIndex = i;
                        console.log('Found ability tab at line', i);
                        break;
                    }
                }

                return {
                    ability_tab_found: abilityTabIndex >= 0,
                    ability_tab_index: abilityTabIndex,
                    line_at_index: abilityTabIndex >= 0 ? lines[abilityTabIndex] : null,
                    next_line: abilityTabIndex >= 0 && abilityTabIndex + 1 < lines.length ? lines[abilityTabIndex + 1] : null,
                };
            }
            """,
            {
                "ability_label": en_config.ability_label,
                "stats_label": en_config.stats_label,
            },
        )

        print(f"\n  English extraction test:")
        print(f"    Ability tab found: {en_extract['ability_tab_found']}")
        print(f"    Ability tab index: {en_extract['ability_tab_index']}")
        print(f"    Line at index: {en_extract['line_at_index']}")
        print(f"    Next line: {en_extract['next_line']}")

        # Vietnamese extraction test
        vi_extract = await page.evaluate(
            """
            (langConfig) => {
                const pageText = document.body.innerText;
                const lines = pageText.split('\\n').map(l => l.trim()).filter(l => l && l.length > 0);

                console.log('VI: Looking for ability tab: ' + langConfig.ability_label);
                console.log('VI: Looking for stats tab: ' + langConfig.stats_label);

                let abilityTabIndex = -1;
                for (let i = 0; i < Math.min(100, lines.length); i++) {
                    if (lines[i] === langConfig.ability_label && lines[i+1] === langConfig.stats_label) {
                        abilityTabIndex = i;
                        console.log('VI: Found ability tab at line', i);
                        break;
                    }
                }

                return {
                    ability_tab_found: abilityTabIndex >= 0,
                    ability_tab_index: abilityTabIndex,
                    line_at_index: abilityTabIndex >= 0 ? lines[abilityTabIndex] : null,
                    next_line: abilityTabIndex >= 0 && abilityTabIndex + 1 < lines.length ? lines[abilityTabIndex + 1] : null,
                };
            }
            """,
            {
                "ability_label": vi_config.ability_label,
                "stats_label": vi_config.stats_label,
            },
        )

        print(f"\n  Vietnamese extraction test:")
        print(f"    Ability tab found: {vi_extract['ability_tab_found']}")
        print(f"    Ability tab index: {vi_extract['ability_tab_index']}")
        print(f"    Line at index: {vi_extract['line_at_index']}")
        print(f"    Next line: {vi_extract['next_line']}")

        await browser.close()

        print("\n" + "=" * 80)
        print("DEBUG COMPLETE")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(debug_params())
