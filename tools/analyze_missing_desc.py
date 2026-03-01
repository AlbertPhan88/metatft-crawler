#!/usr/bin/env python3
"""
Analyze why some units are missing ability descriptions
"""

import asyncio
import sys
import os
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metatft_crawler.utils.browser import switch_language
from src.metatft_crawler.languages.loader import get_language_config


async def check_unit_page(unit_name, unit_url):
    """Check a unit page for ability description and type."""

    lang_config = get_language_config("vi")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto(unit_url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        await switch_language(page, "vi")
        await page.wait_for_timeout(2000)

        # Get full page text
        page_text = await page.evaluate("document.body.innerText")
        lines = page_text.split('\n')

        print(f"\n{'='*100}")
        print(f"Unit: {unit_name}")
        print(f"{'='*100}")

        # Find Ability section
        ability_idx = -1
        for i, line in enumerate(lines):
            if "Kỹ Năng" in line or "Ability" in line:
                ability_idx = i
                break

        if ability_idx >= 0:
            print(f"\nAbility section (lines {ability_idx} to {ability_idx + 20}):")
            for j in range(ability_idx, min(ability_idx + 20, len(lines))):
                print(f"  {j:3d}: {lines[j][:120]}")

        # Look for type info
        print(f"\nLooking for type (first 50 lines):")
        for j in range(0, min(50, len(lines))):
            if any(t in lines[j] for t in lang_config.unit_types):
                print(f"  {j:3d}: {lines[j][:120]}")

        # Look for markers
        print(f"\nLooking for ability markers:")
        found_passive = False
        found_active = False
        for i, line in enumerate(lines):
            if lang_config.passive_marker in line:
                print(f"  {i:3d}: Found Passive marker: {line}")
                found_passive = True
            if lang_config.active_marker in line:
                print(f"  {i:3d}: Found Active marker: {line}")
                found_active = True

        if not found_passive and not found_active:
            print(f"  No Passive/Active markers found!")

        await browser.close()


async def main():
    # Units with missing descriptions
    units = [
        ("Renekton", "https://www.metatft.com/units/Renekton"),
        ("Sylas", "https://www.metatft.com/units/Sylas"),
        ("Zaahen", "https://www.metatft.com/units/Zaahen"),
        ("Volibear", "https://www.metatft.com/units/Volibear"),
        ("Aatrox", "https://www.metatft.com/units/Aatrox"),
        ("Fiddlesticks", "https://www.metatft.com/units/Fiddlesticks"),
        # One with description for comparison
        ("Baron Nashor", "https://www.metatft.com/units/BaronNashor"),
    ]

    for name, url in units:
        await check_unit_page(name, url)


if __name__ == "__main__":
    asyncio.run(main())
