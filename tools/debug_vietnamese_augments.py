#!/usr/bin/env python3
"""
Debug Vietnamese augments page structure
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playwright.async_api import async_playwright
from metatft_crawler.utils.browser import switch_language


async def debug_vi():
    """Debug Vietnamese page structure."""

    base_url = "https://www.metatft.com/augments"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Navigating to augments page...")
        await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        print("Switching to Vietnamese...")
        await switch_language(page, "vi")

        print("Switching to Table view...")
        await page.evaluate("""
            () => {
                const tableDiv = Array.from(document.querySelectorAll('div'))
                    .find(div => div.innerText === 'Table' && div.className.includes('StatOptionChip'));
                if (tableDiv) tableDiv.click();
            }
        """)
        await page.wait_for_timeout(2000)

        # Get page text
        page_text = await page.evaluate("() => document.body.innerText")
        lines = page_text.split('\n')

        print(f"\nTotal lines: {len(lines)}")
        print("\nFirst 150 lines:")
        for i, line in enumerate(lines[:150]):
            print(f"{i:3d}: {line}")

        # Look for header keywords in Vietnamese
        print("\n\nSearching for column headers...")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if any(keyword in stripped for keyword in ['Augment', 'Augmen', 'Tier', 'Rank', 'Type', 'Loại', 'Hạng', 'Tăng']):
                print(f"Line {i}: {line}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_vi())
