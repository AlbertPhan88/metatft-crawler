#!/usr/bin/env python3
"""
Find the Table view and extract augment details
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playwright.async_api import async_playwright


async def find_table_view():
    """Find and use table view to get augment details."""

    base_url = "https://www.metatft.com/augments"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print(f"Navigating to {base_url}...")
        await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        # Look for "Table" text in page
        text_content = await page.evaluate("() => document.body.innerText")
        lines = text_content.split('\n')

        print("Looking for 'Table' view option...")
        for i, line in enumerate(lines):
            if 'Table' in line and i < 100:
                print(f"Line {i}: {line}")
                print("Context:")
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    print(f"  {j}: {lines[j]}")

        # Try to find clickable elements with "Table" text
        print("\nLooking for 'Table' clickable element...")
        result = await page.evaluate("""
            () => {
                // Find element with "Table" text
                const allElements = document.querySelectorAll('*');
                const tableElements = [];

                for (let el of allElements) {
                    if (el.innerText === 'Table' || el.textContent === 'Table') {
                        tableElements.push({
                            tag: el.tagName,
                            class: el.className,
                            onclick: el.onclick ? 'yes' : 'no',
                            text: el.innerText
                        });
                    }
                }

                return tableElements;
            }
        """)

        print(f"Found {len(result)} elements with 'Table' text:")
        for el in result:
            print(f"  {el}")

        # Try clicking on the Table view link
        try:
            # Look for the view selector
            view_selector = await page.evaluate("""
                () => {
                    const allText = document.body.innerText;
                    if (allText.includes('Select View')) {
                        return 'Found Select View';
                    }
                    return 'Not found';
                }
            """)
            print(f"\nSelect View status: {view_selector}")

            # Look for links/buttons after "Select View:"
            links = await page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('a, button'))
                        .filter(el => el.innerText && el.innerText.length < 50)
                        .map(el => ({ text: el.innerText, tag: el.tagName }))
                        .slice(0, 30);
                }
            """)

            print(f"\nFound {len(links)} clickable elements (first 30):")
            for i, link in enumerate(links):
                print(f"  {i}: [{link['tag']}] {link['text']}")

        except Exception as e:
            print(f"Error: {e}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(find_table_view())
