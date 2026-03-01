#!/usr/bin/env python3
"""
Debug Vietnamese augments extraction to find why it stops early
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playwright.async_api import async_playwright
from metatft_crawler.utils.browser import switch_language
from metatft_crawler.languages.loader import get_language_config


async def debug_vi_extraction():
    """Debug Vietnamese extraction."""

    base_url = "https://www.metatft.com/augments"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        await switch_language(page, "vi")

        # Switch to Table view
        await page.evaluate("""
            () => {
                const tableDiv = Array.from(document.querySelectorAll('div'))
                    .find(div => div.innerText === 'Table' && div.className.includes('StatOptionChip'));
                if (tableDiv) tableDiv.click();
            }
        """)
        await page.wait_for_timeout(2000)

        lang_config = get_language_config("vi")

        # Get page text
        page_text = await page.evaluate("() => document.body.innerText")
        lines = page_text.split('\n')

        print(f"Total lines: {len(lines)}")
        print(f"\nFooter keywords: {lang_config.footer_keywords}")

        # Find where extraction starts and stops
        print("\nSearching for table structure...")

        # Look for 'Type' or tier markers
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == 'Type' or (i > 45 and i < 65 and stripped in ['S', 'A', 'B', 'C', 'D']):
                print(f"Line {i}: {line}")

        print("\n\nLooking for footer keywords...")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if any(kw in stripped for kw in lang_config.footer_keywords):
                print(f"Line {i}: {line} (matches: {[kw for kw in lang_config.footer_keywords if kw in stripped]})")
                if i > 300:  # Only show if later in the file
                    break

        print("\n\nAll unique single-letter lines (potential tier markers):")
        tier_lines = []
        for i, line in enumerate(lines):
            if line.strip() in ['S', 'A', 'B', 'C', 'D']:
                tier_lines.append((i, line.strip()))

        print(f"Found {len(tier_lines)} tier markers at lines:")
        for i, (idx, tier) in enumerate(tier_lines[:20]):
            print(f"  {i+1}. Line {idx}: {tier}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_vi_extraction())
