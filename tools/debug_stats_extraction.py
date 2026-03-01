#!/usr/bin/env python3
"""
Debug stats extraction on Vietnamese page
"""

import asyncio
import sys
import os
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metatft_crawler.utils.browser import switch_language
from src.metatft_crawler.languages.loader import get_language_config


async def debug_stats():
    """Debug stats extraction on Vietnamese unit page."""

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Navigate to a unit
        print("Navigating to Baron Nashor (Vietnamese)...")
        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        # Switch to Vietnamese
        await switch_language(page, "vi")
        await page.wait_for_timeout(2000)

        lang_config = get_language_config("vi")

        # Try to click Stats button
        print("\nLooking for Stats button...")
        stats_button = await page.query_selector("button:has-text('Stats')")
        if not stats_button:
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                text = await btn.text_content()
                print(f"  Found button: {text}")
                if text and "Stats" in text or "Số Liệu" in text:
                    stats_button = btn
                    print(f"  ✅ Found Stats button: {text}")
                    break

        if stats_button:
            print("Clicking Stats button...")
            await stats_button.click()
            await page.wait_for_timeout(1000)

            # Get page text
            page_text = await page.evaluate("document.body.innerText")
            lines = page_text.split('\n')

            print(f"\nTotal lines on page: {len(lines)}")
            print("\nFirst 150 lines after clicking Stats:")
            print("-" * 100)
            for i, line in enumerate(lines[:150]):
                if line.strip():
                    print(f"{i:3d}: {line[:100]}")

            # Try to extract stats
            print("\n" + "=" * 100)
            print("STATS EXTRACTION TEST")
            print("=" * 100)

            stats_labels = {
                'health': lang_config.health,
                'mana': lang_config.mana,
                'attack_damage': lang_config.attack_damage,
                'ability_power': lang_config.ability_power,
                'armor': lang_config.armor,
                'magic_resist': lang_config.magic_resist,
            }

            print(f"\nLooking for stat labels: {stats_labels}")

            found_stats = {}
            for label, config_value in stats_labels.items():
                for i, line in enumerate(lines):
                    if line.strip() == config_value and i + 1 < len(lines):
                        found_stats[label] = lines[i + 1].strip()
                        print(f"✅ Found {label} ({config_value}): {found_stats[label]}")
                        break
                if label not in found_stats:
                    print(f"❌ Missing {label} ({config_value})")

        else:
            print("❌ Stats button not found!")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_stats())
