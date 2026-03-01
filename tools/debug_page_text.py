#!/usr/bin/env python3
"""
Debug script to see the actual page text for English vs Vietnamese.
"""

import asyncio
import sys
import os
from playwright.async_api import async_playwright

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metatft_crawler.utils.browser import switch_language


async def debug_page_text():
    """Check the actual page text in both languages."""

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Navigate to Baron Nashor
        print("Navigating to Baron Nashor...")
        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        # Get English page text
        print("\n" + "=" * 80)
        print("ENGLISH PAGE TEXT (Baron Nashor)")
        print("=" * 80)
        en_text = await page.evaluate("document.body.innerText")
        en_lines = en_text.split('\n')

        # Print first 100 lines
        for i, line in enumerate(en_lines[:100]):
            if line.strip():
                print(f"{i:3d}: {line[:100]}")

        # Find ability tab index
        ability_idx = -1
        for i, line in enumerate(en_lines):
            if line.strip() == "Ability":
                ability_idx = i
                break

        print(f"\n📍 Ability tab found at line {ability_idx}")
        if ability_idx > 0:
            print("\nLines around Ability tab (English):")
            for i in range(max(0, ability_idx - 10), min(len(en_lines), ability_idx + 5)):
                marker = ">>> " if i == ability_idx else "    "
                print(f"{marker}{i:3d}: {en_lines[i][:80]}")

        # Switch to Vietnamese
        print("\n" + "=" * 80)
        print("SWITCHING TO VIETNAMESE...")
        print("=" * 80)
        await switch_language(page, "vi")

        # Get Vietnamese page text
        print("\nVIETNAMESE PAGE TEXT (Baron Nashor)")
        print("=" * 80)
        vi_text = await page.evaluate("document.body.innerText")
        vi_lines = vi_text.split('\n')

        # Print first 100 lines
        for i, line in enumerate(vi_lines[:100]):
            if line.strip():
                print(f"{i:3d}: {line[:100]}")

        # Find ability tab index
        ability_idx_vi = -1
        for i, line in enumerate(vi_lines):
            if line.strip() == "Ability":
                ability_idx_vi = i
                break

        print(f"\n📍 Ability tab found at line {ability_idx_vi}")
        if ability_idx_vi > 0:
            print("\nLines around Ability tab (Vietnamese):")
            for i in range(max(0, ability_idx_vi - 10), min(len(vi_lines), ability_idx_vi + 5)):
                marker = ">>> " if i == ability_idx_vi else "    "
                print(f"{marker}{i:3d}: {vi_lines[i][:80]}")

        # Compare structure
        print("\n" + "=" * 80)
        print("STRUCTURE COMPARISON")
        print("=" * 80)

        print("\nENGLISH - 20 lines before Ability tab:")
        en_before = en_lines[max(0, ability_idx - 20) : ability_idx]
        for i, line in enumerate(en_before):
            if line.strip():
                print(f"  {line.strip()[:80]}")

        print("\nVIETNAMESE - 20 lines before Ability tab:")
        vi_before = vi_lines[max(0, ability_idx_vi - 20) : ability_idx_vi]
        for i, line in enumerate(vi_before):
            if line.strip():
                print(f"  {line.strip()[:80]}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_page_text())
