#!/usr/bin/env python3
"""
Get augments from table view
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playwright.async_api import async_playwright


async def get_table_augments():
    """Get augments from table view."""

    base_url = "https://www.metatft.com/augments"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print(f"Navigating to {base_url}...")
        await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        # Click on Table view
        print("Clicking on Table view...")
        try:
            await page.click("div.StatOptionChip:has-text('Table')")
            await page.wait_for_timeout(3000)
            print("Clicked Table view successfully")
        except Exception as e:
            print(f"Error clicking Table: {e}")
            # Try alternative selector
            try:
                await page.evaluate("""
                    () => {
                        const tableDiv = Array.from(document.querySelectorAll('div'))
                            .find(div => div.textContent === 'Table' && div.className.includes('StatOptionChip'));
                        if (tableDiv) tableDiv.click();
                    }
                """)
                await page.wait_for_timeout(3000)
                print("Clicked Table view using alternative method")
            except Exception as e2:
                print(f"Alternative click also failed: {e2}")

        # Get the page content now
        text_content = await page.evaluate("() => document.body.innerText")
        lines = text_content.split('\n')

        print("\n=== PAGE CONTENT (first 100 lines) ===")
        for i, line in enumerate(lines[:100]):
            print(f"{i:3d}: {line}")

        # Look for table structure
        print("\n=== LOOKING FOR TABLE STRUCTURE ===")
        for i, line in enumerate(lines):
            if i > 50 and i < 200:  # Skip header
                if any(keyword in line for keyword in ['Tier', 'Type', 'Pick Rate', 'Win Rate', 'Placement']):
                    print(f"Line {i}: {line}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(get_table_augments())
