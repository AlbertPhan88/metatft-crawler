#!/usr/bin/env python3
"""Debug script to find why descriptions are missing"""

import asyncio
from playwright.async_api import async_playwright


async def check_items():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Try items which should have descriptions
        items_to_check = [
            ('Gold Collector', 'https://www.metatft.com/items/TFT_Item_Artifact_GoldCollector'),
            ('Zhonya\'s Paradox', 'https://www.metatft.com/items/TFT_Item_Artifact_ZhonyasParadox'),
            ('Spirit Visage', 'https://www.metatft.com/items/TFT_Item_Artifact_SpiritVisage'),
        ]

        for item_name, item_url in items_to_check:
            print(f"\n{'='*70}")
            print(f"Checking: {item_name}")
            print(f"URL: {item_url}")
            print('='*70)

            await page.goto(item_url, timeout=60000)
            await page.wait_for_timeout(2000)

            lines = await page.evaluate("""
                () => {
                    const pageText = document.body.innerText;
                    const allLines = pageText.split('\\n').map(l => l.trim()).filter(l => l);
                    return allLines;
                }
            """)

            print(f"Total lines: {len(lines)}\n")

            # Show lines that might contain recipe/stats/description
            for i, line in enumerate(lines):
                if i >= 25 and i <= 50:
                    print(f"{i:3d}: {line}")

        await browser.close()


asyncio.run(check_items())
