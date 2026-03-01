#!/usr/bin/env python3
"""
Find where type information is on the page for units missing it
"""

import asyncio
import sys
import os
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metatft_crawler.utils.browser import switch_language
from src.metatft_crawler.languages.loader import get_language_config


async def find_type(unit_name, unit_url):
    """Find type information on page."""

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

        # Search for type words in entire page
        print(f"\nSearching all {len(lines)} lines for type keywords:")
        type_lines = []
        for i, line in enumerate(lines):
            for type_word in lang_config.unit_types:
                if type_word in line:
                    type_lines.append((i, line, type_word))

        if type_lines:
            for line_num, line_text, matched_word in type_lines:
                print(f"  Line {line_num:3d}: [{matched_word}] {line_text[:100]}")
        else:
            print(f"  NO TYPE KEYWORDS FOUND!")

        await browser.close()


async def main():
    # Units missing type
    units = [
        ("Ziggs", "https://www.metatft.com/units/Ziggs"),
        ("Mel", "https://www.metatft.com/units/Mel"),
        ("Fiddlesticks", "https://www.metatft.com/units/Fiddlesticks"),
        ("Lucian & Senna", "https://www.metatft.com/units/LucianSenna"),
    ]

    for name, url in units:
        await find_type(name, url)


if __name__ == "__main__":
    asyncio.run(main())
