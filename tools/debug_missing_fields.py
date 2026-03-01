#!/usr/bin/env python3
"""
Debug missing ability descriptions and traits
"""

import asyncio
import sys
import os
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metatft_crawler.utils.browser import switch_language
from src.metatft_crawler.languages.loader import get_language_config


async def debug_missing():
    """Debug missing fields on Renekton (has no ability description)."""

    lang_config = get_language_config("vi")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Navigate to Renekton
        print("=" * 100)
        print("Debugging Renekton (missing ability description)")
        print("=" * 100)

        await page.goto("https://www.metatft.com/units/Renekton", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        # Switch to Vietnamese
        await switch_language(page, "vi")
        await page.wait_for_timeout(2000)

        # Get page text to see what's there
        page_text = await page.evaluate("document.body.innerText")
        lines = page_text.split('\n')

        print("\n" + "=" * 100)
        print("Looking for Ability section and description")
        print("=" * 100)

        # Find Ability section
        ability_idx = -1
        for i, line in enumerate(lines):
            if "Kỹ Năng" in line or "Ability" in line:
                print(f"\n✅ Found 'Kỹ Năng'/'Ability' at line {i}: {line}")
                ability_idx = i
                # Print next 30 lines
                print("\nNext 30 lines after Kỹ Năng:")
                for j in range(i, min(i + 30, len(lines))):
                    print(f"  {j:3d}: {lines[j][:100]}")
                break

        print("\n" + "=" * 100)
        print("Looking for Traits")
        print("=" * 100)

        # Look for trait indicators
        for i, line in enumerate(lines):
            if any(trait in line for trait in lang_config.traits):
                print(f"\n✅ Found trait at line {i}: {line}")

        # Also check if there are any lines with Vietnamese trait names
        print("\nSearching for Vietnamese trait names...")
        vi_traits = ["Vật Lý", "Đấu Sĩ", "Hư Không", "Tai Ương", "Phép Thuật", "Xạ Thủ",
                     "Zaun", "Người Zaun", "Tí Hon", "Bắn Xa", "Thoái Ích Chủ", "Tiên Tri",
                     "Hiệp Sĩ", "Sát Thủ", "Pháp Sư", "Cung Thủ", "Hỗ Trợ", "Quân Áo", "Rú Thổ"]

        found_traits = False
        for i, line in enumerate(lines):
            for trait in vi_traits:
                if trait in line:
                    print(f"  Line {i}: {line}")
                    found_traits = True
                    break

        if not found_traits:
            print("  No Vietnamese trait names found on page!")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_missing())
