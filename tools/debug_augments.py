#!/usr/bin/env python3
"""
Debug script to inspect augments page structure
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playwright.async_api import async_playwright
from metatft_crawler.utils.browser import switch_language


async def debug_augments():
    """Debug the augments page structure."""

    base_url = "https://www.metatft.com/augments"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print(f"Navigating to {base_url}...")
        try:
            await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Navigation timeout: {e}")

        print("Waiting for page to fully render...")
        await page.wait_for_timeout(5000)

        # Get the page text
        page_text = await page.content()

        # Save the HTML to a file for inspection
        with open("/tmp/augments_page.html", "w") as f:
            f.write(page_text)
        print("Saved page HTML to /tmp/augments_page.html")

        # Get page text content
        text_content = await page.evaluate("() => document.body.innerText")

        # Save text content
        with open("/tmp/augments_text.txt", "w") as f:
            f.write(text_content)
        print("Saved page text to /tmp/augments_text.txt")

        # Print first 2000 chars of text
        print("\n=== PAGE TEXT (first 2000 chars) ===")
        print(text_content[:2000])

        # Look for augment names
        print("\n=== Looking for tier indicators ===")
        lines = text_content.split('\n')
        for i, line in enumerate(lines[:100]):
            if any(tier in line for tier in ['Bronze', 'Silver', 'Gold', 'Prismatic', 'Radiant', 'Tier']):
                print(f"Line {i}: {line}")
                # Print surrounding context
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    print(f"  {j}: {lines[j]}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_augments())
