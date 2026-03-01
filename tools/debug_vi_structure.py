#!/usr/bin/env python3
"""Debug Vietnamese items page structure"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from playwright.async_api import async_playwright
from metatft_crawler.utils.browser import switch_language


async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Navigate to items page...")
        await page.goto('https://www.metatft.com/items', timeout=60000)
        await page.wait_for_timeout(3000)

        print("Switch to Vietnamese...")
        await switch_language(page, "vi")

        # Get first item URL
        first_item = await page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a[href*="/items/"]'));
                const itemLinks = links.filter(a => {
                    const href = a.getAttribute('href') || '';
                    return href.startsWith('/items/') && !href.endsWith('/items');
                });
                if (itemLinks.length > 0) {
                    return {
                        name: itemLinks[0].innerText.trim(),
                        url: itemLinks[0].getAttribute('href')
                    };
                }
                return null;
            }
        """)

        if first_item:
            print(f"\nFirst item: {first_item['name']}")
            print(f"URL: {first_item['url']}")

            # Navigate to first item in Vietnamese
            await page.goto(f"https://www.metatft.com{first_item['url']}", timeout=60000)
            await page.wait_for_timeout(2000)

            # Check page content
            lines = await page.evaluate("""
                () => {
                    const pageText = document.body.innerText;
                    const allLines = pageText.split('\\n').map(l => l.trim()).filter(l => l);
                    return allLines.slice(25, 60);
                }
            """)

            print("\nPage lines 25-60:")
            for i, line in enumerate(lines, 25):
                print(f"{i:3d}: {line}")

            # Check for "TFT Item Stats" equivalent in Vietnamese
            full_lines = await page.evaluate("""
                () => {
                    const pageText = document.body.innerText;
                    const allLines = pageText.split('\\n').map(l => l.trim()).filter(l => l);
                    return allLines;
                }
            """)

            print("\n\nSearching for stats/recipe patterns:")
            for i, line in enumerate(full_lines):
                if 'TFT' in line or 'Recipe' in line or 'Công Thức' in line or 'Công thức' in line:
                    print(f"{i}: {line}")

        await browser.close()


asyncio.run(check())
